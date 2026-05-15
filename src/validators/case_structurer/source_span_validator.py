"""Strict source span validation for Case Structurer output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.case_structurer.source_span import SourceSpan
from src.validators.case_structurer.source_span_utils import (
    StructuredSourceObject,
    combined_existing_span_text,
    get_all_structured_objects,
    offsets_in_bounds,
    quoted_text_exists,
    range_inside_any_parent,
    resolved_range,
    section_range_map,
    span_slice_matches,
    unsupported_item_fields,
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


class StrictSourceSpanValidator:
    """Validate source spans against the final assembled raw input."""

    def validate(
        self,
        result: CaseStructuringResult,
    ) -> SourceSpanValidationReport:
        """Validate all source spans in the CaseStructuringResult."""
        issues: list[SourceSpanValidationIssue] = []
        raw_text = result.input.raw_text
        expected_input_id = result.input.input_id

        for structured_object in get_all_structured_objects(result):
            issues.extend(
                self._validate_required_source_spans(structured_object)
            )

            for span in structured_object.source_spans:
                issues.extend(
                    self._validate_span(
                        raw_text=raw_text,
                        expected_input_id=expected_input_id,
                        structured_object=structured_object,
                        span=span,
                    )
                )

        issues.extend(self._validate_item_spans_inside_parent_sections(result))
        issues.extend(self._validate_source_level_time_texts(result))
        issues.extend(self._validate_structured_item_source_support(result))

        is_valid = not any(
            issue.severity == ValidationSeverity.ERROR for issue in issues
        )

        return SourceSpanValidationReport(is_valid=is_valid, issues=issues)

    def _validate_required_source_spans(
        self,
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
        self,
        raw_text: str,
        expected_input_id: str,
        structured_object: StructuredSourceObject,
        span: SourceSpan,
    ) -> list[SourceSpanValidationIssue]:
        issues: list[SourceSpanValidationIssue] = []
        text_exists = quoted_text_exists(raw_text, span.quoted_text)

        if span.input_id != expected_input_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="source_span_input_id_mismatch",
                    message=(
                        "SourceSpan.input_id must equal "
                        "result.input.input_id."
                    ),
                    structured_object=structured_object,
                    span=span,
                )
            )

        if not text_exists:
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
                self._validate_resolved_offsets(
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
        self,
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

    def _validate_item_spans_inside_parent_sections(
        self,
        result: CaseStructuringResult,
    ) -> list[SourceSpanValidationIssue]:
        issues: list[SourceSpanValidationIssue] = []
        raw_text = result.input.raw_text
        section_ranges = section_range_map(result, raw_text)

        for item in result.structured_items:
            parent_ranges = section_ranges.get(item.section_id, [])
            if not parent_ranges:
                continue

            structured_object = StructuredSourceObject(
                object_type="StructuredClinicalItem",
                object_id=item.item_id,
                source_spans=item.source_spans,
                parent_section_id=item.section_id,
            )

            for span in item.source_spans:
                item_range = resolved_range(span, raw_text)
                if item_range is None:
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

        return issues

    def _validate_source_level_time_texts(
        self,
        result: CaseStructuringResult,
    ) -> list[SourceSpanValidationIssue]:
        issues: list[SourceSpanValidationIssue] = []
        raw_text = result.input.raw_text

        for item in result.structured_items:
            if item.time_text is None or quoted_text_exists(raw_text, item.time_text):
                continue

            issues.append(
                SourceSpanValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="source_time_text_not_found",
                    message=(
                        "StructuredClinicalItem.time_text must be an original "
                        "source text expression, not a synthesized or inferred "
                        "time phrase."
                    ),
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                    quoted_text=item.time_text,
                )
            )

        for event in result.timeline_events:
            if event.event_time_text is None or quoted_text_exists(
                raw_text,
                event.event_time_text,
            ):
                continue

            issues.append(
                SourceSpanValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="source_time_text_not_found",
                    message=(
                        "TimelineEvent.event_time_text must be an original "
                        "source text expression, not a synthesized or inferred "
                        "time phrase."
                    ),
                    object_type="TimelineEvent",
                    object_id=event.event_id,
                    quoted_text=event.event_time_text,
                )
            )

        return issues

    def _validate_structured_item_source_support(
        self,
        result: CaseStructuringResult,
    ) -> list[SourceSpanValidationIssue]:
        issues: list[SourceSpanValidationIssue] = []
        raw_text = result.input.raw_text

        for item in result.structured_items:
            source_text = combined_existing_span_text(raw_text, item.source_spans)
            if not source_text:
                continue

            unsupported_fields = unsupported_item_fields(item, source_text)
            if not unsupported_fields:
                continue

            issues.append(
                SourceSpanValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="item_source_span_insufficient_support",
                    message=(
                        "StructuredClinicalItem fields are not sufficiently "
                        "supported by the item's source_spans. Unsupported "
                        f"fields: {', '.join(unsupported_fields)}."
                    ),
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                    quoted_text=source_text,
                )
            )

        return issues


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
