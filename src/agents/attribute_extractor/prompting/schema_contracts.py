from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Any

from src.schemas.attribute_extractor.attribute_role import AttributeRole
from src.schemas.attribute_extractor.common import ConfidenceLevel, ValidationSeverity


def attribute_span_role_labeling_contract() -> dict[str, Any]:
    return {
        "allowed_attribute_role_values": _format_enum_values(AttributeRole),
        "allowed_confidence_values": _format_enum_values(ConfidenceLevel),
        "allowed_warning_severity_values": _format_enum_values(ValidationSeverity),
        "attribute_span_fields": _lines(
            [
                "source_item_id",
                "span_text",
                "attribute_role",
                "normalized_value",
                "normalized_unit",
                "normalized_text",
                "extraction_confidence",
                "notes",
            ]
        ),
        "warning_fields": _lines(
            [
                "severity",
                "code",
                "message",
                "related_item_id",
                "related_attribute_id",
            ]
        ),
    }


def _format_enum_values(enum_cls: type[StrEnum]) -> str:
    return _lines(item.value for item in enum_cls)


def _lines(values: Iterable[str]) -> str:
    return "\n".join(f"- {value}" for value in values)
