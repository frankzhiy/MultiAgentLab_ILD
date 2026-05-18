"""Strict source span validation for Case Structurer output."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.validators.case_structurer.source_span_utils import (
    StructuredSourceObject,
    find_resolvable_span_pieces,
    offsets_in_bounds,
    quoted_text_exists,
    range_inside_any_parent,
    resolved_range,
    span_slice_matches,
)


class SourceSpanValidationIssue(BaseModel):
    """One source span validation issue."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    severity: ValidationSeverity
    code: str
    message: str
    object_type: str
    object_id: str
    span_id: str | None = None
    quoted_text: str | None = None


class SourceSpanValidationReport(BaseModel):
    """Validation report for all source spans in a CaseStructuringResult."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    is_valid: bool
    issues: list[SourceSpanValidationIssue] = Field(default_factory=list)


class SectionSourceSpanValidator:
    """Validate ClinicalSection source spans against the raw input."""

    def validate(
        self,
        raw_text: str,
        expected_input_id: str,
        sections: Sequence[ClinicalSection],
    ) -> SourceSpanValidationReport:
        issues: list[SourceSpanValidationIssue] = []

        for section in sections:
            structured_object = StructuredSourceObject(
                object_type="ClinicalSection",
                object_id=section.section_id,
                source_spans=section.source_spans,
            )
            issues.extend(
                _validate_required_source_spans(structured_object)
            )

            for span in structured_object.source_spans:
                issues.extend(
                    _validate_span(
                        raw_text=raw_text,
                        expected_input_id=expected_input_id,
                        structured_object=structured_object,
                        span=span,
                        synthetic_code="section_quoted_text_discontinuous_or_synthetic",
                    )
                )

        is_valid = not any(
            issue.severity == ValidationSeverity.ERROR for issue in issues
        )

        return SourceSpanValidationReport(is_valid=is_valid, issues=issues)


class ItemSourceSpanValidator:
    """Validate StructuredClinicalItem source spans against section grounding."""

    def validate(
        self,
        raw_text: str,
        expected_input_id: str,
        sections: Sequence[ClinicalSection],
        items: Sequence[StructuredClinicalItem],
    ) -> SourceSpanValidationReport:
        issues: list[SourceSpanValidationIssue] = []
        section_ids = {section.section_id for section in sections}
        section_ranges = _section_range_map_from_sections(sections, raw_text)

        for item in items:
            structured_object = StructuredSourceObject(
                object_type="StructuredClinicalItem",
                object_id=item.item_id,
                source_spans=item.source_spans,
                parent_section_id=item.section_id,
            )
            if item.section_id not in section_ids:
                issues.append(
                    SourceSpanValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="item_parent_section_not_found",
                        message=(
                            "StructuredClinicalItem.section_id must reference "
                            "an existing ClinicalSection."
                        ),
                        object_type="StructuredClinicalItem",
                        object_id=item.item_id,
                    )
                )

            issues.extend(
                _validate_required_source_spans(structured_object)
            )

            for span in item.source_spans:
                issues.extend(
                    _validate_span(
                        raw_text=raw_text,
                        expected_input_id=expected_input_id,
                        structured_object=structured_object,
                        span=span,
                    )
                )

                item_range = resolved_range(span, raw_text)
                parent_ranges = section_ranges.get(item.section_id, [])
                if item_range is None or not parent_ranges:
                    continue

                if not range_inside_any_parent(item_range, parent_ranges):
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.WARNING,
                            code="item_span_outside_parent_section",
                            message=(
                                "StructuredClinicalItem source span is outside "
                                "all resolved source spans for its parent "
                                "ClinicalSection."
                            ),
                            structured_object=structured_object,
                            span=span,
                        )
                    )

        is_valid = not any(
            issue.severity == ValidationSeverity.ERROR for issue in issues
        )

        return SourceSpanValidationReport(is_valid=is_valid, issues=issues)


def _validate_required_source_spans(
    structured_object: StructuredSourceObject,
) -> list[SourceSpanValidationIssue]:
    if structured_object.source_spans:
        return []

    return [
        _issue(
            severity=ValidationSeverity.ERROR,
            code="missing_source_span",
            message=(
                f"{structured_object.object_type} must include at least "
                "one source_span."
            ),
            structured_object=structured_object,
        )
    ]


def _validate_span(
    raw_text: str,
    expected_input_id: str,
    structured_object: StructuredSourceObject,
    span: SourceSpan,
    synthetic_code: str | None = None,
) -> list[SourceSpanValidationIssue]:
    issues: list[SourceSpanValidationIssue] = []
    text_exists = quoted_text_exists(raw_text, span.quoted_text)

    if span.input_id != expected_input_id:
        issues.append(
            _issue(
                severity=ValidationSeverity.ERROR,
                code="source_span_input_id_mismatch",
                message=(
                    "SourceSpan.input_id must equal result.input.input_id."
                ),
                structured_object=structured_object,
                span=span,
            )
        )

    if not text_exists:
        piece_ranges = find_resolvable_span_pieces(raw_text, span.quoted_text)
        if synthetic_code is not None and len(piece_ranges) > 1:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code=synthetic_code,
                    message=(
                        "SourceSpan.quoted_text was not found as one raw_text "
                        "span, but multiple exact pieces were found in "
                        "different raw_text locations."
                    ),
                    structured_object=structured_object,
                    span=span,
                )
            )
        else:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="quoted_text_not_found",
                    message=(
                        "SourceSpan.quoted_text was not found in raw_text, "
                        "even after whitespace normalization."
                    ),
                    structured_object=structured_object,
                    span=span,
                )
            )

    if span.char_start is not None and span.char_end is not None:
        issues.extend(
            _validate_resolved_offsets(
                raw_text=raw_text,
                structured_object=structured_object,
                span=span,
            )
        )
    elif text_exists and span.char_start is None and span.char_end is None:
        issues.append(
            _issue(
                severity=ValidationSeverity.WARNING,
                code="unresolved_offsets",
                message=(
                    "SourceSpan.quoted_text exists in raw_text, but "
                    "char_start and char_end were not resolved."
                ),
                structured_object=structured_object,
                span=span,
            )
        )

    return issues


def _validate_resolved_offsets(
    raw_text: str,
    structured_object: StructuredSourceObject,
    span: SourceSpan,
) -> list[SourceSpanValidationIssue]:
    issues: list[SourceSpanValidationIssue] = []
    char_start = span.char_start
    char_end = span.char_end

    if char_start is None or char_end is None:
        return issues

    if not offsets_in_bounds(raw_text, char_start, char_end):
        issues.append(
            _issue(
                severity=ValidationSeverity.ERROR,
                code="char_offsets_out_of_bounds",
                message=(
                    "SourceSpan.char_start and char_end must be inside "
                    "raw_text bounds."
                ),
                structured_object=structured_object,
                span=span,
            )
        )
        return issues

    if not span_slice_matches(
        raw_text=raw_text,
        quoted_text=span.quoted_text,
        char_start=char_start,
        char_end=char_end,
    ):
        issues.append(
            _issue(
                severity=ValidationSeverity.ERROR,
                code="char_offsets_do_not_match_quoted_text",
                message=(
                    "SourceSpan.char_start and char_end slice does not "
                    "match quoted_text."
                ),
                structured_object=structured_object,
                span=span,
            )
        )

    return issues


def _section_range_map_from_sections(
    sections: Sequence[ClinicalSection],
    raw_text: str,
) -> dict[str, list[tuple[int, int]]]:
    ranges: dict[str, list[tuple[int, int]]] = {}
    for section in sections:
        for span in section.source_spans:
            span_range = resolved_range(span, raw_text)
            if span_range is not None:
                ranges.setdefault(section.section_id, []).append(span_range)
    return ranges


def _issue(
    severity: ValidationSeverity,
    code: str,
    message: str,
    structured_object: StructuredSourceObject,
    span: SourceSpan | None = None,
) -> SourceSpanValidationIssue:
    return SourceSpanValidationIssue(
        severity=severity,
        code=code,
        message=message,
        object_type=structured_object.object_type,
        object_id=structured_object.object_id,
        span_id=span.span_id if span is not None else None,
        quoted_text=span.quoted_text if span is not None else None,
    )
