from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionWarning,
)
from src.schemas.attribute_extractor.common import ValidationSeverity
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.source_span import SourceSpan
from src.validators.case_structurer.source_span_utils import quoted_text_exists


class AttributeDraftPayload(BaseModel):
    """Internal attribute draft payload after deterministic span validation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    attribute_payloads: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[AttributeExtractionWarning] = Field(default_factory=list)


class AttributeSpanValidator:
    """Validate LLM attribute spans and resolve raw-text provenance."""

    def validate(
        self,
        structuring_result: CaseStructuringResult,
        draft_payload: dict[str, Any],
    ) -> AttributeDraftPayload:
        warnings: list[AttributeExtractionWarning] = []
        attributes: list[dict[str, Any]] = []
        items_by_id = {
            item.item_id: item
            for item in structuring_result.structured_items
        }

        for index, draft in enumerate(draft_payload.get("attribute_spans") or [], start=1):
            if not isinstance(draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_attribute_span",
                        message="Attribute span draft was not a JSON object.",
                    )
                )
                continue

            forbidden_fields = sorted(
                set(draft) & {"value", "unit", "time_text", "body_site"}
            )
            if forbidden_fields:
                warnings.append(
                    _warning(
                        code="forbidden_attribute_fields_ignored",
                        message=(
                            "Attribute span draft contained forbidden fields "
                            f"that were ignored: {forbidden_fields}."
                        ),
                        related_item_id=_optional_text(draft.get("source_item_id")),
                    )
                )

            source_item_id = _optional_text(draft.get("source_item_id"))
            if source_item_id is None or source_item_id not in items_by_id:
                warnings.append(
                    _warning(
                        code="unknown_source_item_id",
                        message=(
                            "Attribute span draft referenced a source_item_id "
                            "that does not exist and was skipped."
                        ),
                        related_item_id=source_item_id,
                    )
                )
                continue

            span_text = _optional_text(draft.get("span_text"))
            if span_text is None:
                warnings.append(
                    _warning(
                        code="missing_span_text",
                        message="Attribute span draft had empty span_text and was skipped.",
                        related_item_id=source_item_id,
                    )
                )
                continue

            item = items_by_id[source_item_id]
            item_source_text = _item_source_text(item)
            if span_text not in item_source_text:
                warnings.append(
                    _warning(
                        code="span_text_not_in_item_source_text",
                        message=(
                            "Attribute span_text must be a continuous substring "
                            "of the source item's source text."
                        ),
                        related_item_id=source_item_id,
                    )
                )
                continue

            source_span = _resolve_attribute_source_span(
                structuring_result=structuring_result,
                source_item_id=source_item_id,
                span_text=span_text,
                index=index,
            )
            if source_span is None:
                warnings.append(
                    _warning(
                        code="span_text_not_in_raw_text",
                        message=(
                            "Attribute span_text could not be located in raw_text "
                            "and was skipped."
                        ),
                        related_item_id=source_item_id,
                    )
                )
                continue

            attributes.append(
                {
                    "source_item_id": source_item_id,
                    "span_text": span_text,
                    "attribute_role": draft.get("attribute_role"),
                    "source_span": source_span.model_dump(mode="python"),
                    "normalized_value": draft.get("normalized_value"),
                    "normalized_unit": draft.get("normalized_unit"),
                    "normalized_text": draft.get("normalized_text"),
                    "extraction_confidence": draft.get("extraction_confidence"),
                    "notes": draft.get("notes"),
                }
            )

        for warning_draft in draft_payload.get("extraction_warnings") or []:
            if not isinstance(warning_draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_extraction_warning",
                        message="Extraction warning draft was not a JSON object.",
                    )
                )
                continue
            warnings.append(
                _warning(
                    code=_optional_text(warning_draft.get("code"))
                    or "llm_attribute_warning",
                    message=_optional_text(warning_draft.get("message"))
                    or "LLM reported an attribute extraction warning.",
                    severity=_severity(warning_draft.get("severity")),
                    related_item_id=_optional_text(
                        warning_draft.get("related_item_id")
                    ),
                    related_attribute_id=_optional_text(
                        warning_draft.get("related_attribute_id")
                    ),
                )
            )

        return AttributeDraftPayload(attribute_payloads=attributes, warnings=warnings)


def _item_source_text(item: Any) -> str:
    return "\n".join(span.quoted_text for span in item.source_spans)


def _resolve_attribute_source_span(
    *,
    structuring_result: CaseStructuringResult,
    source_item_id: str,
    span_text: str,
    index: int,
) -> SourceSpan | None:
    raw_text = structuring_result.input.raw_text
    item = next(
        item
        for item in structuring_result.structured_items
        if item.item_id == source_item_id
    )

    for parent_span in item.source_spans:
        local_start = parent_span.quoted_text.find(span_text)
        if local_start < 0:
            continue
        if parent_span.char_start is not None:
            char_start = parent_span.char_start + local_start
            char_end = char_start + len(span_text)
        else:
            char_start = raw_text.find(span_text)
            char_end = char_start + len(span_text) if char_start >= 0 else -1
        if char_start < 0 or not quoted_text_exists(raw_text, span_text):
            continue
        return SourceSpan(
            span_id=f"span_attr_{index:03d}",
            input_id=structuring_result.input.input_id,
            quoted_text=span_text,
            char_start=char_start,
            char_end=char_end,
        )

    char_start = raw_text.find(span_text)
    if char_start < 0:
        return None
    return SourceSpan(
        span_id=f"span_attr_{index:03d}",
        input_id=structuring_result.input.input_id,
        quoted_text=span_text,
        char_start=char_start,
        char_end=char_start + len(span_text),
    )


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _severity(value: Any) -> ValidationSeverity:
    if isinstance(value, ValidationSeverity):
        return value
    if isinstance(value, str):
        for severity in ValidationSeverity:
            if value == severity.value:
                return severity
    return ValidationSeverity.WARNING


def _warning(
    *,
    code: str,
    message: str,
    severity: ValidationSeverity = ValidationSeverity.WARNING,
    related_item_id: str | None = None,
    related_attribute_id: str | None = None,
) -> AttributeExtractionWarning:
    return AttributeExtractionWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_attribute_id=related_attribute_id,
    )
