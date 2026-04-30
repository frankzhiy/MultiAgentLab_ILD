from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent


@dataclass(frozen=True)
class NormalizedSections:
    sections: list[ClinicalSection]
    id_map: dict[str, str]


@dataclass(frozen=True)
class NormalizedItems:
    items: list[StructuredClinicalItem]
    id_map: dict[str, str]


@dataclass(frozen=True)
class NormalizedTemporalAmbiguities:
    timeline_events: list[TimelineEvent]
    ambiguities: list[AmbiguityItem]
    event_id_map: dict[str, str]
    ambiguity_id_map: dict[str, str]


def _normalize_span_input_ids(
    source_spans: list[SourceSpan],
    raw_input: RawTextInput,
) -> list[SourceSpan]:
    return [
        span.model_copy(update={"input_id": raw_input.input_id})
        for span in source_spans
    ]


class SectionNormalizer:
    """Enforce deterministic section ids and text order."""

    def normalize(
        self,
        sections: list[ClinicalSection],
        raw_input: RawTextInput,
    ) -> NormalizedSections:
        id_map = {
            section.section_id: f"section_{index:03d}"
            for index, section in enumerate(sections, start=1)
        }

        normalized_sections: list[ClinicalSection] = []
        for index, section in enumerate(sections, start=1):
            new_section_id = id_map[section.section_id]
            parent_section_id = (
                id_map.get(section.parent_section_id)
                if section.parent_section_id is not None
                else None
            )
            normalized_sections.append(
                section.model_copy(
                    update={
                        "section_id": new_section_id,
                        "input_id": raw_input.input_id,
                        "section_order": index,
                        "parent_section_id": parent_section_id,
                        "source_spans": _normalize_span_input_ids(
                            section.source_spans,
                            raw_input,
                        ),
                    }
                )
            )

        return NormalizedSections(sections=normalized_sections, id_map=id_map)


class ItemNormalizer:
    """Enforce deterministic item ids, text order, and section references."""

    def normalize(
        self,
        items: list[StructuredClinicalItem],
        raw_input: RawTextInput,
        valid_section_ids: set[str],
    ) -> NormalizedItems:
        invalid_section_refs = [
            item.section_id
            for item in items
            if item.section_id not in valid_section_ids
        ]
        if invalid_section_refs:
            raise ValueError(
                "StructuredClinicalItem.section_id must reference an existing "
                f"ClinicalSection.section_id. Invalid refs: {invalid_section_refs}"
            )

        id_map = {
            item.item_id: f"item_{index:03d}"
            for index, item in enumerate(items, start=1)
        }

        normalized_items = [
            item.model_copy(
                update={
                    "item_id": id_map[item.item_id],
                    "input_id": raw_input.input_id,
                    "item_order": index,
                    "source_spans": _normalize_span_input_ids(
                        item.source_spans,
                        raw_input,
                    ),
                }
            )
            for index, item in enumerate(items, start=1)
        ]

        return NormalizedItems(items=normalized_items, id_map=id_map)


class TimelineAmbiguityNormalizer:
    """Normalize timeline event and ambiguity ids and references."""

    def normalize(
        self,
        timeline_events: list[TimelineEvent],
        ambiguities: list[AmbiguityItem],
        raw_input: RawTextInput,
        valid_section_ids: set[str],
        valid_item_ids: set[str],
        section_id_map: Mapping[str, str] | None = None,
        item_id_map: Mapping[str, str] | None = None,
    ) -> NormalizedTemporalAmbiguities:
        section_id_map = section_id_map or {}
        item_id_map = item_id_map or {}

        event_id_map = {
            event.event_id: f"event_{index:03d}"
            for index, event in enumerate(timeline_events, start=1)
        }
        ambiguity_id_map = {
            ambiguity.ambiguity_id: f"ambiguity_{index:03d}"
            for index, ambiguity in enumerate(ambiguities, start=1)
        }

        normalized_events: list[TimelineEvent] = []
        for index, event in enumerate(timeline_events, start=1):
            related_item_ids = self._align_references(
                ids=event.related_item_ids,
                id_map=item_id_map,
                valid_ids=valid_item_ids,
                label="TimelineEvent.related_item_ids",
            )
            normalized_events.append(
                event.model_copy(
                    update={
                        "event_id": event_id_map[event.event_id],
                        "input_id": raw_input.input_id,
                        "event_order": index,
                        "related_item_ids": related_item_ids,
                        "source_spans": _normalize_span_input_ids(
                            event.source_spans,
                            raw_input,
                        ),
                    }
                )
            )

        normalized_ambiguities: list[AmbiguityItem] = []
        for ambiguity in ambiguities:
            related_section_ids = self._align_references(
                ids=ambiguity.related_section_ids,
                id_map=section_id_map,
                valid_ids=valid_section_ids,
                label="AmbiguityItem.related_section_ids",
            )
            related_item_ids = self._align_references(
                ids=ambiguity.related_item_ids,
                id_map=item_id_map,
                valid_ids=valid_item_ids,
                label="AmbiguityItem.related_item_ids",
            )
            normalized_ambiguities.append(
                ambiguity.model_copy(
                    update={
                        "ambiguity_id": ambiguity_id_map[ambiguity.ambiguity_id],
                        "input_id": raw_input.input_id,
                        "related_section_ids": related_section_ids,
                        "related_item_ids": related_item_ids,
                        "source_spans": _normalize_span_input_ids(
                            ambiguity.source_spans,
                            raw_input,
                        ),
                    }
                )
            )

        return NormalizedTemporalAmbiguities(
            timeline_events=normalized_events,
            ambiguities=normalized_ambiguities,
            event_id_map=event_id_map,
            ambiguity_id_map=ambiguity_id_map,
        )

    @staticmethod
    def _align_references(
        ids: list[str],
        id_map: Mapping[str, str],
        valid_ids: set[str],
        label: str,
    ) -> list[str]:
        aligned_ids = [id_map.get(object_id, object_id) for object_id in ids]
        invalid_ids = [object_id for object_id in aligned_ids if object_id not in valid_ids]
        if invalid_ids:
            raise ValueError(f"{label} contains invalid refs: {invalid_ids}")
        return aligned_ids
