from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


class AtomizationCandidate(BaseModel):
    """Compact LLM-ready representation of one StructuredClinicalItem."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: str
    item_type: str
    label: str
    value: str | None = None
    unit: str | None = None
    body_site: str | None = None
    temporality: str
    time_text: str | None = None
    certainty: str
    negation: str
    source_spans: list[dict[str, Any]] = Field(default_factory=list)
    section_id: str
    section_type: str | None = None
    section_title: str | None = None
    source_text: str


class AtomizationCandidateBuilder:
    """Build compact atomization candidates from a CaseStructuringResult."""

    def build(
        self,
        structuring_result: CaseStructuringResult,
    ) -> list[AtomizationCandidate]:
        sections_by_id = {
            section.section_id: section
            for section in structuring_result.clinical_sections
        }

        candidates: list[AtomizationCandidate] = []
        for item in structuring_result.structured_items:
            section = sections_by_id.get(item.section_id)
            source_spans = [
                {
                    "span_id": span.span_id,
                    "input_id": span.input_id,
                    "quoted_text": span.quoted_text,
                    "char_start": span.char_start,
                    "char_end": span.char_end,
                }
                for span in item.source_spans
            ]
            source_text = "\n".join(
                span["quoted_text"]
                for span in source_spans
                if isinstance(span.get("quoted_text"), str)
            )

            candidates.append(
                AtomizationCandidate(
                    item_id=item.item_id,
                    item_type=_value(item.item_type),
                    label=item.label,
                    value=item.value,
                    unit=item.unit,
                    body_site=item.body_site,
                    temporality=_value(item.temporality),
                    time_text=item.time_text,
                    certainty=_value(item.certainty),
                    negation=_value(item.negation),
                    source_spans=source_spans,
                    section_id=item.section_id,
                    section_type=_value(section.section_type) if section else None,
                    section_title=section.title if section else None,
                    source_text=source_text,
                )
            )

        return candidates


def _value(value: object) -> str:
    return getattr(value, "value", str(value))
