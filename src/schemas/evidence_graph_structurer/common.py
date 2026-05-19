"""Shared primitive types, enums, and helpers for Evidence Graph Structurer schemas.

Evidence Graph Structurer converts validated Case Structurer output into
source-grounded local clinical evidence graphlets (frames + nodes + typed
relations) for later reasoning phases.

It does not assign support/refute relationships to diagnoses, generate
hypotheses, recommend treatment, resolve conflicts, perform update tracing,
run safety gates, or arbitrate between agents.
"""

import re

from src.schemas.case_structurer.common import (
    CaseID,
    CertaintyLevel,
    ConfidenceLevel,
    InputID,
    ItemID,
    NegationStatus,
    SpanID,
    StageID,
    TemporalRelation,
    ValidationSeverity,
)

__all__ = [
    "CaseID",
    "CertaintyLevel",
    "ConfidenceLevel",
    "FORBIDDEN_REASONING_FIELD_NAMES",
    "FORBIDDEN_REASONING_TEXT_PATTERNS",
    "InputID",
    "ItemID",
    "NegationStatus",
    "SpanID",
    "StageID",
    "TemporalRelation",
    "ValidationSeverity",
    "normalize_optional_text",
    "reject_reasoning_scope_text",
    "require_non_empty_text",
    "validate_no_forbidden_schema_fields",
]


FORBIDDEN_REASONING_FIELD_NAMES = frozenset(
    {
        "diagnosis",
        "hypothesis_id",
        "supports",
        "refutes",
        "action",
        "treatment",
        "conflict",
        "update_trace",
        "safety_gate",
        "arbitration",
    }
)

FORBIDDEN_REASONING_TEXT_PATTERNS = (
    re.compile(
        r"\b(?:support|supports|supported|refute|refutes|refuted)\b"
        r"(?:\W+\w+){0,6}?\W+\b(?:diagnosis|hypothesis)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:diagnosis|hypothesis)\b(?:\W+\w+){0,3}?\W+\bis\s+"
        r"(?:supported|refuted)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:final|most likely)\s+diagnosis\b", re.IGNORECASE),
    re.compile(r"\bdiagnosis\s+is\b", re.IGNORECASE),
    re.compile(r"\brecommend(?:s|ed|ing)?\s+treatment\b", re.IGNORECASE),
    re.compile(r"\btreatment\s+recommendation\b", re.IGNORECASE),
    re.compile(r"\bshould\s+treat\b", re.IGNORECASE),
    re.compile(r"\bmanagement\s+plan\b", re.IGNORECASE),
    re.compile(r"\baction\s+plan\b", re.IGNORECASE),
    re.compile(r"\bupdate\s+decision\b", re.IGNORECASE),
    re.compile(r"\bupdate\s+trace\b", re.IGNORECASE),
    re.compile(r"\bconflict\s+(?:is\s+)?resolved\b", re.IGNORECASE),
    re.compile(r"\bconflict\s+resolution\b", re.IGNORECASE),
    re.compile(r"\bsafety\s+gate\s+(?:passed|failed)\b", re.IGNORECASE),
    re.compile(r"\barbitration\s+result\b", re.IGNORECASE),
)


def normalize_optional_text(value: str | None) -> str | None:
    """Normalize blank optional text values to None."""
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    return cleaned


def require_non_empty_text(value: str, field_name: str) -> str:
    """Reject empty or whitespace-only required text."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty.")

    return cleaned


def reject_reasoning_scope_text(value: str | None, field_name: str) -> str | None:
    """Reject text that crosses into downstream reasoning responsibilities."""
    cleaned = normalize_optional_text(value)
    if cleaned is None:
        return None

    forbidden_patterns = [
        pattern.pattern
        for pattern in FORBIDDEN_REASONING_TEXT_PATTERNS
        if pattern.search(cleaned)
    ]

    if forbidden_patterns:
        raise ValueError(
            f"{field_name} must describe evidence-structuring quality only and "
            "must not include explicit downstream judgment or action patterns "
            "such as diagnosis/hypothesis support or refutation, diagnosis "
            "selection, treatment recommendation, conflict resolution, action "
            "plan, update decision, safety gate result, or arbitration result. "
            f"Forbidden patterns: {forbidden_patterns}"
        )

    return cleaned


def validate_no_forbidden_schema_fields(
    model_name: str,
    field_names: set[str],
) -> None:
    """Validate that a schema does not expose downstream-reasoning fields."""
    forbidden_fields = sorted(field_names & FORBIDDEN_REASONING_FIELD_NAMES)
    if forbidden_fields:
        raise ValueError(
            f"{model_name} must not define downstream reasoning fields: "
            f"{forbidden_fields}"
        )
