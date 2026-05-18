"""Clinical Assertion Validator.

Source-grounds and shape-checks the LLM-produced ClinicalObjectAssertion payload
for one ItemContext. The validator is conservative: invalid drafts are dropped
with a warning rather than repaired. Hardcoded Chinese cue/term lists have been
removed — the LLM, guided by the prompt, is responsible for choosing
status/object_type/structural fields.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.schemas.case_structurer.common import ConfidenceLevel
from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
    ClinicalObjectAssertion,
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_tree_structurer.common import ValidationSeverity
from src.schemas.evidence_tree_structurer.tree_structuring_warning import (
    TreeStructuringWarning,
)

from .item_context import ItemContext


class ClinicalAssertionValidator:
    """Validate one LLM payload into a typed ClinicalAssertionResolutionResult."""

    def validate(
        self,
        context: ItemContext,
        payload: dict[str, Any],
    ) -> ClinicalAssertionResolutionResult:
        warnings: list[TreeStructuringWarning] = []
        raw_assertions = payload.get("clinical_object_assertions")
        if not isinstance(raw_assertions, list):
            warnings.append(
                _warning(
                    severity=ValidationSeverity.ERROR,
                    code="clinical_assertion_payload_invalid",
                    message=(
                        "LLM payload is missing a list field "
                        "'clinical_object_assertions'."
                    ),
                    related_item_id=context.item_id,
                )
            )
            return ClinicalAssertionResolutionResult(
                clinical_object_assertions=[],
                assertion_warnings=warnings,
            )

        valid_span_ids = set(context.span_ids)
        cleaned_assertions: list[ClinicalObjectAssertion] = []
        seen_object_texts: set[str] = set()

        for index, raw in enumerate(raw_assertions):
            if not isinstance(raw, dict):
                warnings.append(
                    _warning(
                        severity=ValidationSeverity.WARNING,
                        code="clinical_assertion_dropped_invalid_shape",
                        message=(
                            f"Assertion #{index} dropped: expected a JSON object."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue

            assertion, drop_reason = _coerce_assertion(
                raw,
                context=context,
                valid_span_ids=valid_span_ids,
            )
            if assertion is None:
                warnings.append(
                    _warning(
                        severity=ValidationSeverity.WARNING,
                        code="clinical_assertion_dropped",
                        message=(
                            f"Assertion #{index} dropped: {drop_reason}"
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue

            dedupe_key = (
                assertion.object_text,
                assertion.assertion_status.value,
                assertion.temporal_anchor_text or "",
                assertion.trigger_text or "",
            )
            if dedupe_key in seen_object_texts:
                continue
            seen_object_texts.add(dedupe_key)
            cleaned_assertions.append(assertion)

        # Forward any LLM-emitted warnings that are well-formed.
        for raw_warning in payload.get("assertion_warnings", []) or []:
            if not isinstance(raw_warning, dict):
                continue
            try:
                warnings.append(TreeStructuringWarning(**raw_warning))
            except ValidationError:
                continue

        return ClinicalAssertionResolutionResult(
            clinical_object_assertions=cleaned_assertions,
            assertion_warnings=warnings,
        )


def _coerce_assertion(
    raw: dict[str, Any],
    *,
    context: ItemContext,
    valid_span_ids: set[str],
) -> tuple[ClinicalObjectAssertion | None, str]:
    object_text = _str(raw.get("object_text"))
    if not object_text:
        return None, "object_text is empty"
    if object_text not in context.source_text:
        return None, "object_text is not a substring of source_text"

    cue = _optional_str(raw.get("assertion_cue_text"))
    if cue is not None and cue not in context.source_text:
        cue = None
    scope = _optional_str(raw.get("assertion_scope_text"))
    if scope is not None and scope not in context.source_text:
        scope = None

    temporal_anchor_text = _optional_str(raw.get("temporal_anchor_text"))
    if temporal_anchor_text is not None and temporal_anchor_text not in context.source_text:
        temporal_anchor_text = None
    trigger_text = _optional_str(raw.get("trigger_text"))
    if trigger_text is not None and trigger_text not in context.source_text:
        trigger_text = None

    modifier_texts_raw = raw.get("modifier_texts") or []
    modifier_texts: list[str] = []
    if isinstance(modifier_texts_raw, list):
        for modifier in modifier_texts_raw:
            text = _optional_str(modifier)
            if text is not None and text in context.source_text and text not in modifier_texts:
                modifier_texts.append(text)

    object_type = _enum(
        raw.get("object_type"),
        ClinicalObjectType,
        default=ClinicalObjectType.OTHER,
    )
    assertion_status = _enum(
        raw.get("assertion_status"),
        ClinicalObjectAssertionStatus,
        default=ClinicalObjectAssertionStatus.UNCERTAIN,
    )

    confidence = _enum(
        raw.get("confidence"),
        ConfidenceLevel,
        default=ConfidenceLevel.MEDIUM,
    )

    source_span_ids_raw = raw.get("source_span_ids") or []
    source_span_ids: list[str] = []
    if isinstance(source_span_ids_raw, list):
        for span_id in source_span_ids_raw:
            sid = _optional_str(span_id)
            if sid is not None and sid in valid_span_ids and sid not in source_span_ids:
                source_span_ids.append(sid)
    if not source_span_ids and context.span_ids:
        source_span_ids = list(context.span_ids)

    notes = _optional_str(raw.get("notes"))

    context_text = scope or object_text

    try:
        assertion = ClinicalObjectAssertion(
            source_item_id=context.item_id,
            object_text=object_text,
            object_type=object_type,
            assertion_status=assertion_status,
            assertion_cue_text=cue,
            assertion_scope_text=scope,
            temporal_anchor_text=temporal_anchor_text,
            trigger_text=trigger_text,
            modifier_texts=modifier_texts,
            context_text=context_text,
            source_span_ids=source_span_ids,
            confidence=confidence,
            notes=notes,
        )
    except ValidationError as exc:
        return None, f"pydantic validation failed: {exc.errors()[0].get('msg', '?')}"

    return assertion, ""


def _str(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return None


def _optional_str(value: Any) -> str | None:
    return _str(value)


def _enum(value: Any, enum_type: type, default: Any) -> Any:
    if isinstance(value, str):
        try:
            return enum_type(value.strip())
        except ValueError:
            return default
    return default


def _warning(
    *,
    severity: ValidationSeverity,
    code: str,
    message: str,
    related_item_id: str | None = None,
    related_span_id: str | None = None,
) -> TreeStructuringWarning:
    return TreeStructuringWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_span_id=related_span_id,
    )
