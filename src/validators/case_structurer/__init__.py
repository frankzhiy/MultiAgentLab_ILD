"""Validators for Case Structurer outputs."""

from .source_span_corrector import (
    CaseStructuringSourceSpanResult,
    ItemSourceSpanCorrector,
    ItemSourceSpanValidationCorrectionResult,
    SectionSourceSpanCorrector,
    SectionSourceSpanValidationCorrectionResult,
    SourceSpanCorrectionAction,
    SourceSpanCorrectionReport,
    validate_and_correct_item_spans,
    validate_and_correct_section_spans,
)
from .source_span_utils import (
    get_all_structured_objects,
    normalize_text_for_match,
    quoted_text_exists,
    span_slice_matches,
)
from .source_span_validator import (
    ItemSourceSpanValidator,
    SectionSourceSpanValidator,
    SourceSpanValidationIssue,
    SourceSpanValidationReport,
)

__all__ = [
    "CaseStructuringSourceSpanResult",
    "ItemSourceSpanCorrector",
    "ItemSourceSpanValidationCorrectionResult",
    "ItemSourceSpanValidator",
    "SectionSourceSpanCorrector",
    "SectionSourceSpanValidationCorrectionResult",
    "SectionSourceSpanValidator",
    "SourceSpanCorrectionAction",
    "SourceSpanCorrectionReport",
    "SourceSpanValidationIssue",
    "SourceSpanValidationReport",
    "get_all_structured_objects",
    "normalize_text_for_match",
    "quoted_text_exists",
    "span_slice_matches",
    "validate_and_correct_item_spans",
    "validate_and_correct_section_spans",
]
