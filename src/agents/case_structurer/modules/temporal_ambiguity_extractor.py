from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem, AmbiguityType
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.common import ConfidenceLevel, TimeExpressionType
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import StageContext
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent, TimelineEventType

from .base_llm_extractor import BaseLLMExtractor


class TemporalAmbiguityExtractionResult(BaseModel):
    """Internal temporal/ambiguity extraction payload."""

    model_config = ConfigDict(extra="forbid")

    timeline_events: list[TimelineEvent] = Field(default_factory=list)
    ambiguities: list[AmbiguityItem] = Field(default_factory=list)


class TemporalAmbiguityExtractor(BaseLLMExtractor):
    """Extract chronology and source-level ambiguity only."""

    def extract(
        self,
        raw_input: RawTextInput,
        stage_context: StageContext,
        sections: list[ClinicalSection],
        items: list[StructuredClinicalItem],
    ) -> TemporalAmbiguityExtractionResult:
        content = self.generate_json(
            prompt_path=self.prompt_path("temporal_ambiguity"),
            user_payload={
                "raw_input": raw_input.model_dump(mode="json"),
                "stage_context": stage_context.model_dump(mode="json"),
                "clinical_sections": [
                    {
                        "section_id": section.section_id,
                        "section_type": section.section_type,
                        "title": section.title,
                        "normalized_text": section.normalized_text,
                        "section_order": section.section_order,
                    }
                    for section in sections
                ],
                "structured_items": [
                    {
                        "item_id": item.item_id,
                        "section_id": item.section_id,
                        "item_type": item.item_type,
                        "label": item.label,
                        "value": item.value,
                        "time_text": item.time_text,
                        "item_order": item.item_order,
                    }
                    for item in items
                ],
            },
            instruction=(
                "Return exactly one JSON object with keys timeline_events and "
                "ambiguities."
            ),
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("TemporalAmbiguityExtractor expected a JSON object.")

        event_payloads = payload.get("timeline_events") or []
        ambiguity_payloads = payload.get("ambiguities") or []
        if not isinstance(event_payloads, list):
            raise ValueError("timeline_events must be a JSON array.")
        if not isinstance(ambiguity_payloads, list):
            raise ValueError("ambiguities must be a JSON array.")

        valid_section_ids = {section.section_id for section in sections}
        valid_item_ids = {item.item_id for item in items}

        hydrated_payload = {
            "timeline_events": [
                self._hydrate_event_payload(raw_input, event, index, valid_item_ids)
                for index, event in enumerate(event_payloads, start=1)
                if isinstance(event, dict)
            ],
            "ambiguities": [
                self._hydrate_ambiguity_payload(
                    raw_input,
                    ambiguity,
                    index,
                    valid_section_ids,
                    valid_item_ids,
                )
                for index, ambiguity in enumerate(ambiguity_payloads, start=1)
                if isinstance(ambiguity, dict)
            ],
        }
        return TemporalAmbiguityExtractionResult.model_validate(hydrated_payload)

    def _hydrate_event_payload(
        self,
        raw_input: RawTextInput,
        payload: dict[str, Any],
        index: int,
        valid_item_ids: set[str],
    ) -> dict[str, Any]:
        description = self.first_text(
            payload,
            ("description", "event_description", "text", "quoted_text"),
        )
        if description is None:
            source_spans = payload.get("source_spans") or []
            if isinstance(source_spans, list) and source_spans:
                first_span = source_spans[0]
                if isinstance(first_span, dict):
                    description = self.first_text(
                        first_span,
                        ("quoted_text", "source_text", "text", "fragment"),
                    )

        if description is None:
            raise ValueError(
                "TimelineEvent payload is missing description or an equivalent "
                "text field."
            )

        event_time_text = payload.get("event_time_text")
        time_expression_type = self.coerce_enum_value(
            payload.get("time_expression_type"),
            TimeExpressionType,
            "unknown",
        )
        if event_time_text is None:
            time_expression_type = "unknown"

        related_item_ids = payload.get("related_item_ids") or []
        if not isinstance(related_item_ids, list):
            related_item_ids = []
        related_item_ids = [
            item_id for item_id in related_item_ids if item_id in valid_item_ids
        ]

        return {
            "event_id": payload.get("event_id") or f"event_{index:03d}",
            "input_id": raw_input.input_id,
            "event_type": self.coerce_enum_value(
                payload.get("event_type"),
                TimelineEventType,
                "unknown",
            ),
            "event_time_text": event_time_text,
            "time_expression_type": time_expression_type,
            "normalized_time": payload.get("normalized_time"),
            "relative_time": payload.get("relative_time"),
            "description": description,
            "related_item_ids": related_item_ids,
            "source_spans": self.prepare_source_spans(
                raw_input=raw_input,
                payload=payload,
                default_quoted_text=description,
                span_prefix=f"span_event_{index:03d}",
            ),
            "event_order": index,
            "classification_confidence": self.coerce_enum_value(
                payload.get("classification_confidence"),
                ConfidenceLevel,
                "medium",
            ),
            "notes": payload.get("notes"),
        }

    def _hydrate_ambiguity_payload(
        self,
        raw_input: RawTextInput,
        payload: dict[str, Any],
        index: int,
        valid_section_ids: set[str],
        valid_item_ids: set[str],
    ) -> dict[str, Any]:
        ambiguous_text = self.first_text(
            payload,
            ("ambiguous_text", "text", "statement", "quoted_text"),
        )
        if ambiguous_text is None:
            source_spans = payload.get("source_spans") or []
            if isinstance(source_spans, list) and source_spans:
                first_span = source_spans[0]
                if isinstance(first_span, dict):
                    ambiguous_text = self.first_text(
                        first_span,
                        ("quoted_text", "source_text", "text", "fragment"),
                    )

        if ambiguous_text is None:
            raise ValueError(
                "AmbiguityItem payload is missing ambiguous_text or an "
                "equivalent text field."
            )

        possible_interpretations = payload.get("possible_interpretations") or []
        if not isinstance(possible_interpretations, list):
            possible_interpretations = [str(possible_interpretations)]
        possible_interpretations = [
            item.strip()
            for item in possible_interpretations
            if isinstance(item, str) and item.strip()
        ]
        if not possible_interpretations:
            possible_interpretations = [
                "The source text is ambiguous or under-specified."
            ]

        related_section_ids = payload.get("related_section_ids") or []
        if not isinstance(related_section_ids, list):
            related_section_ids = []
        related_section_ids = [
            section_id
            for section_id in related_section_ids
            if section_id in valid_section_ids
        ]

        related_item_ids = payload.get("related_item_ids") or []
        if not isinstance(related_item_ids, list):
            related_item_ids = []
        related_item_ids = [
            item_id for item_id in related_item_ids if item_id in valid_item_ids
        ]

        return {
            "ambiguity_id": (
                payload.get("ambiguity_id") or f"ambiguity_{index:03d}"
            ),
            "input_id": raw_input.input_id,
            "ambiguity_type": self.coerce_enum_value(
                payload.get("ambiguity_type"),
                AmbiguityType,
                "other",
            ),
            "ambiguous_text": ambiguous_text,
            "possible_interpretations": possible_interpretations,
            "reason": (
                payload.get("reason")
                or "The source text should not be forced into one interpretation."
            ),
            "related_section_ids": related_section_ids,
            "related_item_ids": related_item_ids,
            "source_spans": self.prepare_source_spans(
                raw_input=raw_input,
                payload=payload,
                default_quoted_text=ambiguous_text,
                span_prefix=f"span_ambiguity_{index:03d}",
            ),
            "needs_clarification": bool(payload.get("needs_clarification", False)),
            "classification_confidence": self.coerce_enum_value(
                payload.get("classification_confidence"),
                ConfidenceLevel,
                "medium",
            ),
            "notes": payload.get("notes"),
        }
