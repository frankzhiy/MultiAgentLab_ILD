from __future__ import annotations

from src.validators.case_structurer.source_span_utils import (
    item_field_supported_by_source,
    quoted_text_exists,
)


def ground_item_text_field(
    field_name: str,
    value: str | None,
    raw_text: str,
) -> str | None:
    """Keep an optional item text field only when raw_text can support it."""
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    if item_field_supported_by_source(field_name, cleaned, raw_text):
        return cleaned
    return None


def ground_source_text(value: str | None, raw_text: str) -> str | None:
    """Keep a source-level text value only when it appears in raw_text."""
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    if quoted_text_exists(raw_text, cleaned):
        return cleaned
    return None
