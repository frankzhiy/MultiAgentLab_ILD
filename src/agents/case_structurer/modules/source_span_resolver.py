from __future__ import annotations

from dataclasses import dataclass

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent


@dataclass(frozen=True)
class ResolvedSourceObjects:
    sections: list[ClinicalSection]
    items: list[StructuredClinicalItem]
    timeline_events: list[TimelineEvent]
    ambiguities: list[AmbiguityItem]


class SourceSpanResolver:
    """Resolve exact quoted_text offsets against the raw input."""

    def resolve(
        self,
        raw_input: RawTextInput,
        sections: list[ClinicalSection],
        items: list[StructuredClinicalItem],
        timeline_events: list[TimelineEvent],
        ambiguities: list[AmbiguityItem],
    ) -> ResolvedSourceObjects:
        span_counter = 0

        def resolve_spans(spans: list[SourceSpan]) -> list[SourceSpan]:
            nonlocal span_counter
            resolved: list[SourceSpan] = []
            for span in spans:
                span_counter += 1
                span_id = span.span_id
                if not str(span_id).strip():
                    span_id = f"span_{span_counter:03d}"

                start = raw_input.raw_text.find(span.quoted_text)
                if start >= 0:
                    char_start: int | None = start
                    char_end: int | None = start + len(span.quoted_text)
                else:
                    char_start = None
                    char_end = None

                resolved.append(
                    span.model_copy(
                        update={
                            "span_id": span_id,
                            "input_id": raw_input.input_id,
                            "char_start": char_start,
                            "char_end": char_end,
                        }
                    )
                )
            return resolved

        return ResolvedSourceObjects(
            sections=[
                section.model_copy(
                    update={"source_spans": resolve_spans(section.source_spans)}
                )
                for section in sections
            ],
            items=[
                item.model_copy(
                    update={"source_spans": resolve_spans(item.source_spans)}
                )
                for item in items
            ],
            timeline_events=[
                event.model_copy(
                    update={"source_spans": resolve_spans(event.source_spans)}
                )
                for event in timeline_events
            ],
            ambiguities=[
                ambiguity.model_copy(
                    update={"source_spans": resolve_spans(ambiguity.source_spans)}
                )
                for ambiguity in ambiguities
            ],
        )
