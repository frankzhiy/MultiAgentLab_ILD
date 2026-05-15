from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


class ClinicalAttributeSummary(BaseModel):
    """Compact LLM-ready representation of one ClinicalAttribute relation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    attribute_id: str
    attribute_role: str
    attribute_scope: str
    span_text: str
    applies_to_text: str | None = None
    context_text: str
    normalized_value: str | int | float | None = None
    normalized_unit: str | None = None
    normalized_text: str | None = None


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
    temporality: str
    certainty: str
    negation: str
    attributes: list[ClinicalAttributeSummary] = Field(default_factory=list)
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
        attribute_result: AttributeExtractionResult,
    ) -> list[AtomizationCandidate]:
        sections_by_id = {
            section.section_id: section
            for section in structuring_result.clinical_sections
        }
        attributes_by_item_id: dict[str, list[ClinicalAttributeSummary]] = {}
        for attribute in attribute_result.clinical_attributes:
            attributes_by_item_id.setdefault(attribute.source_item_id, []).append(
                ClinicalAttributeSummary(
                    attribute_id=attribute.attribute_id,
                    attribute_role=_value(attribute.attribute_role),
                    attribute_scope=_value(attribute.attribute_scope),
                    span_text=attribute.span_text,
                    applies_to_text=attribute.applies_to_text,
                    context_text=attribute.context_text,
                    normalized_value=attribute.normalized_value,
                    normalized_unit=attribute.normalized_unit,
                    normalized_text=attribute.normalized_text,
                )
            )

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
                    temporality=_value(item.temporality),
                    certainty=_value(item.certainty),
                    negation=_value(item.negation),
                    attributes=attributes_by_item_id.get(item.item_id, []),
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
