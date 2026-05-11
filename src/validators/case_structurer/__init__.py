"""Validators for Case Structurer outputs."""

from .source_span_corrector import (
    DeterministicSourceSpanCorrector,
    SourceSpanCorrectionAction,
    SourceSpanCorrectionReport,
    SourceSpanValidationCorrectionResult,
    validate_and_correct_source_spans,
)
from .source_span_utils import (
    get_all_structured_objects,
    normalize_text_for_match,
    quoted_text_exists,
    span_slice_matches,
)
from .source_span_validator import (
    StrictSourceSpanValidator,
    SourceSpanValidationIssue,
    SourceSpanValidationReport,
)

__all__ = [
    "DeterministicSourceSpanCorrector",
    "SourceSpanCorrectionAction",
    "SourceSpanCorrectionReport",
    "SourceSpanValidationCorrectionResult",
    "StrictSourceSpanValidator",
    "SourceSpanValidationIssue",
    "SourceSpanValidationReport",
    "get_all_structured_objects",
    "normalize_text_for_match",
    "quoted_text_exists",
    "span_slice_matches",
    "validate_and_correct_source_spans",
]
