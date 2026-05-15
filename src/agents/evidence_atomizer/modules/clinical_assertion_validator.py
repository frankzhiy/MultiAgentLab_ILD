from __future__ import annotations

from typing import Any

from src.schemas.case_structurer.common import ConfidenceLevel, ValidationSeverity
from src.schemas.evidence_atomizer import AtomizationWarning
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
    ClinicalObjectAssertion,
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)

from .atomization_candidate_builder import AtomizationCandidate


class ClinicalAssertionValidator:
    """Validate LLM clinical assertion drafts against one source candidate."""

    def validate(
        self,
        candidate: AtomizationCandidate,
        payload: Any,
    ) -> ClinicalAssertionResolutionResult:
        warnings: list[AtomizationWarning] = []
        assertions: list[ClinicalObjectAssertion] = []
        source_text = candidate.source_text.strip()
        span_ids = _span_ids(candidate)

        for draft in _extract_assertion_drafts(payload, candidate, warnings):
            object_text = _optional_text(draft.get("object_text"))
            if object_text is None:
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_object_text_missing",
                        message=(
                            "Clinical assertion draft was dropped because object_text "
                            "was empty."
                        ),
                    )
                )
                continue

            if object_text not in source_text:
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_object_not_grounded",
                        message=(
                            "Clinical assertion draft was dropped because object_text "
                            "was not a contiguous substring of source_text."
                        ),
                    )
                )
                continue

            source_item_id = _optional_text(draft.get("source_item_id"))
            if source_item_id != candidate.item_id:
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_assertion_source_item_corrected",
                        message=(
                            "Clinical assertion source_item_id did not match the "
                            "candidate item_id and was corrected."
                        ),
                    )
                )

            object_type = _coerce_object_type(draft.get("object_type"))
            if object_type == ClinicalObjectType.UNCERTAIN:
                raw_object_type = _optional_text(draft.get("object_type"))
                if raw_object_type not in {None, ClinicalObjectType.UNCERTAIN.value}:
                    warnings.append(
                        _warning(
                            candidate,
                            code="clinical_object_type_corrected",
                            message=(
                                "Clinical assertion object_type was invalid and "
                                "was corrected to uncertain."
                            ),
                        )
                    )

            assertion_status = _coerce_assertion_status(draft.get("assertion_status"))
            raw_assertion_status = _optional_text(draft.get("assertion_status"))
            if (
                assertion_status == ClinicalObjectAssertionStatus.UNCERTAIN
                and raw_assertion_status
                not in {
                    ClinicalObjectAssertionStatus.UNCERTAIN.value,
                    None,
                }
            ):
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_assertion_status_corrected",
                        message=(
                            "Clinical assertion status was invalid and was "
                            "corrected to uncertain."
                        ),
                    )
                )

            cue_text = _ground_optional_text(
                candidate,
                source_text,
                _optional_text(draft.get("assertion_cue_text")),
                field_name="assertion_cue_text",
                warning_code="clinical_assertion_cue_not_grounded",
                warnings=warnings,
            )
            scope_text = _ground_optional_text(
                candidate,
                source_text,
                _optional_text(draft.get("assertion_scope_text")),
                field_name="assertion_scope_text",
                warning_code="clinical_assertion_scope_not_grounded",
                warnings=warnings,
            )

            if _optional_text(draft.get("context_text")) not in {None, source_text}:
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_assertion_context_corrected",
                        message=(
                            "Clinical assertion context_text did not match the "
                            "candidate source_text and was corrected."
                        ),
                    )
                )

            confidence = _coerce_confidence(draft.get("confidence"))
            raw_confidence = _optional_text(draft.get("confidence"))
            if raw_confidence not in {
                None,
                ConfidenceLevel.LOW.value,
                ConfidenceLevel.MEDIUM.value,
                ConfidenceLevel.HIGH.value,
            }:
                warnings.append(
                    _warning(
                        candidate,
                        code="clinical_assertion_confidence_corrected",
                        message=(
                            "Clinical assertion confidence was invalid and was "
                            "corrected to medium."
                        ),
                    )
                )

            assertion = ClinicalObjectAssertion(
                source_item_id=candidate.item_id,
                object_text=object_text,
                object_type=object_type,
                assertion_status=assertion_status,
                assertion_cue_text=cue_text,
                assertion_scope_text=scope_text,
                context_text=source_text,
                source_span_ids=span_ids,
                confidence=confidence,
                notes=_optional_text(draft.get("notes")),
            )
            if assertion not in assertions:
                assertions.append(assertion)

        warnings.extend(_normalize_warning_drafts(candidate, payload))
        return ClinicalAssertionResolutionResult(
            clinical_object_assertions=assertions,
            assertion_warnings=warnings,
        )


def _extract_assertion_drafts(
    payload: Any,
    candidate: AtomizationCandidate,
    warnings: list[AtomizationWarning],
) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        drafts = payload
    elif isinstance(payload, dict):
        drafts = payload.get("clinical_object_assertions", [])
    else:
        warnings.append(
            _warning(
                candidate,
                code="clinical_assertion_payload_invalid",
                message="Clinical assertion payload was not a JSON object or array.",
            )
        )
        return []

    if not isinstance(drafts, list):
        warnings.append(
            _warning(
                candidate,
                code="clinical_assertion_list_missing",
                message=(
                    "Clinical assertion payload was corrected because "
                    "clinical_object_assertions was not a list."
                ),
            )
        )
        return []

    result: list[dict[str, Any]] = []
    for draft in drafts:
        if isinstance(draft, dict):
            result.append(draft)
            continue
        warnings.append(
            _warning(
                candidate,
                code="clinical_assertion_draft_invalid",
                message="Clinical assertion draft was dropped because it was not an object.",
            )
        )
    return result


def _normalize_warning_drafts(
    candidate: AtomizationCandidate,
    payload: Any,
) -> list[AtomizationWarning]:
    if not isinstance(payload, dict):
        return []

    warning_drafts = payload.get("assertion_warnings", [])
    if not isinstance(warning_drafts, list):
        return [
            _warning(
                candidate,
                code="clinical_assertion_warnings_invalid",
                message="Assertion warnings payload was not a list.",
            )
        ]

    warnings: list[AtomizationWarning] = []
    for warning_draft in warning_drafts:
        if not isinstance(warning_draft, dict):
            warnings.append(
                _warning(
                    candidate,
                    code="clinical_assertion_warning_invalid",
                    message="Assertion warning draft was not an object.",
                )
            )
            continue

        warnings.append(
            AtomizationWarning(
                severity=_coerce_severity(warning_draft.get("severity")),
                code=_optional_text(warning_draft.get("code"))
                or "clinical_assertion_warning",
                message=_optional_text(warning_draft.get("message"))
                or "Clinical assertion resolver reported a warning.",
                related_item_id=candidate.item_id,
                related_span_id=_span_ids(candidate)[0] if _span_ids(candidate) else None,
            )
        )
    return warnings


def _ground_optional_text(
    candidate: AtomizationCandidate,
    source_text: str,
    text: str | None,
    *,
    field_name: str,
    warning_code: str,
    warnings: list[AtomizationWarning],
) -> str | None:
    if text is None:
        return None
    if text in source_text:
        return text

    warnings.append(
        _warning(
            candidate,
            code=warning_code,
            message=(
                f"Clinical assertion {field_name} was not a contiguous substring of "
                "source_text and was cleared."
            ),
        )
    )
    return None


def _coerce_object_type(value: Any) -> ClinicalObjectType:
    if isinstance(value, ClinicalObjectType):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        for member in ClinicalObjectType:
            if member.value == cleaned:
                return member
    return ClinicalObjectType.UNCERTAIN


def _coerce_assertion_status(value: Any) -> ClinicalObjectAssertionStatus:
    if isinstance(value, ClinicalObjectAssertionStatus):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        for member in ClinicalObjectAssertionStatus:
            if member.value == cleaned:
                return member
    return ClinicalObjectAssertionStatus.UNCERTAIN


def _coerce_confidence(value: Any) -> ConfidenceLevel:
    if isinstance(value, ConfidenceLevel):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        for member in ConfidenceLevel:
            if member.value == cleaned:
                return member
    return ConfidenceLevel.MEDIUM


def _coerce_severity(value: Any) -> ValidationSeverity:
    if isinstance(value, ValidationSeverity):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        for member in ValidationSeverity:
            if member.value == cleaned:
                return member
    return ValidationSeverity.WARNING


def _warning(
    candidate: AtomizationCandidate,
    *,
    code: str,
    message: str,
) -> AtomizationWarning:
    span_ids = _span_ids(candidate)
    return AtomizationWarning(
        severity=ValidationSeverity.WARNING,
        code=code,
        message=message,
        related_item_id=candidate.item_id,
        related_span_id=span_ids[0] if span_ids else None,
    )


def _span_ids(candidate: AtomizationCandidate) -> list[str]:
    span_ids: list[str] = []
    for span in candidate.source_spans:
        span_id = span.get("span_id")
        if isinstance(span_id, str) and span_id.strip() and span_id not in span_ids:
            span_ids.append(span_id)
    return span_ids


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    cleaned = value.strip()
    return cleaned or None