"""Internal item-level context passed into the Evidence Tree Structurer modules.

This replaces the deprecated TreeStructuringCandidate pydantic wrapper. It is a
plain immutable dataclass — its only job is to bundle one StructuredClinicalItem
together with its joined source_text and section metadata for downstream
modules (resolver, validator, builder, tree validator).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


@dataclass(frozen=True)
class ItemContext:
    """One StructuredClinicalItem plus its section context and source_text."""

    item_id: str
    item_type: str
    label: str
    temporality: str
    certainty: str
    negation: str
    section_id: str
    section_type: str | None
    section_title: str | None
    source_text: str
    span_ids: tuple[str, ...]
    spans: tuple[dict[str, Any], ...] = field(default_factory=tuple)


def build_item_contexts(
    structuring_result: CaseStructuringResult,
) -> list[ItemContext]:
    """Build one ItemContext per StructuredClinicalItem."""

    sections_by_id = {
        section.section_id: section
        for section in structuring_result.clinical_sections
    }
    contexts: list[ItemContext] = []
    for item in structuring_result.structured_items:
        section = sections_by_id.get(item.section_id)
        spans = tuple(
            {
                "span_id": span.span_id,
                "input_id": span.input_id,
                "quoted_text": span.quoted_text,
                "char_start": span.char_start,
                "char_end": span.char_end,
            }
            for span in item.source_spans
        )
        source_text = "\n".join(
            str(span["quoted_text"])
            for span in spans
            if isinstance(span.get("quoted_text"), str)
        )
        contexts.append(
            ItemContext(
                item_id=item.item_id,
                item_type=_value(item.item_type),
                label=item.label,
                temporality=_value(item.temporality),
                certainty=_value(item.certainty),
                negation=_value(item.negation),
                section_id=item.section_id,
                section_type=_value(section.section_type) if section else None,
                section_title=section.title if section else None,
                source_text=source_text,
                span_ids=tuple(span["span_id"] for span in spans),
                spans=spans,
            )
        )
    return contexts


def _value(value: object) -> str:
    return getattr(value, "value", str(value))
