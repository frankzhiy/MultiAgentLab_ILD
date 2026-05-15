from __future__ import annotations

from enum import StrEnum
from typing import Any

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


def build_attribute_item_payload(result: CaseStructuringResult) -> list[dict[str, Any]]:
    """Build compact LLM payload from source-level structured items."""
    items: list[dict[str, Any]] = []
    for item in result.structured_items:
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
        items.append(
            {
                "item_id": item.item_id,
                "item_type": _value(item.item_type),
                "label": item.label,
                "source_text": source_text,
                "source_spans": source_spans,
            }
        )
    return items


def format_attribute_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "(none)"
    lines: list[str] = []
    for item in items:
        lines.append(
            " | ".join(
                [
                    f"item_id={item['item_id']}",
                    f"item_type={item['item_type']}",
                    f"label={_compact_text(str(item['label']))}",
                    f"source_text={_compact_text(str(item['source_text']))}",
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def format_attribute_boundary() -> str:
    return "\n".join(
        [
            "- Attribute Extractor performs extractive span role labeling.",
            "- It selects continuous original spans from StructuredClinicalItem.source_text.",
            "- It assigns semantic attribute_role values to copied spans.",
            "- It may add lightweight normalized_value, normalized_unit, or normalized_text.",
            "- It does not create evidence atoms, downstream reasoning objects, diagnoses, or treatment advice.",
            "- It must not output fields named value, unit, or time_text.",
        ]
    )


def _value(value: Any) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


def _compact_text(text: str, limit: int = 160) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return f"{compacted[: limit - 3]}..."
