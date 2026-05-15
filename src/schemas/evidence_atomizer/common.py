"""Shared primitive types, enums, and helpers for Evidence Atomizer schemas.

Evidence Atomizer converts validated Case Structurer output into minimal,
source-grounded evidence materials for later reasoning phases.

It creates EvidenceAtom objects, but it does not assign support/refute
relationships to diagnoses, generate hypotheses, recommend treatment,
resolve conflicts, perform update tracing, run safety gates, or arbitrate
between agents.
"""

import re
from enum import StrEnum
from typing import TypeAlias

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
    "AtomizationTransformationType",
    "CaseID",
    "CertaintyLevel",
    "ClinicalDomain",
    "ConfidenceLevel",
    "DeferredReason",
    "EvidenceAtomizationResultID",
    "EvidenceGranularity",
    "EvidenceID",
    "EvidenceType",
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


# ---------------------------------------------------------------------
# ID aliases
# ---------------------------------------------------------------------

EvidenceID: TypeAlias = str
EvidenceAtomizationResultID: TypeAlias = str


# ---------------------------------------------------------------------
# Evidence atomizer categories
# ---------------------------------------------------------------------

class EvidenceType(StrEnum):
    """Clinical evidence type without diagnostic hypothesis labels.

    These values describe the source-level material being atomized. They
    must not encode diagnoses such as IPF, CTD-ILD, fibrotic HP, infection,
    acute exacerbation, or any support/refute relationship to those diagnoses.
    """

    DEMOGRAPHIC = "demographic"
    SYMPTOM = "symptom"
    SIGN = "sign"
    COMORBIDITY = "comorbidity"
    DIAGNOSIS_HISTORY = "diagnosis_history"
    LAB_RESULT = "lab_result"
    IMAGING_FINDING = "imaging_finding"
    PATHOLOGY_FINDING = "pathology_finding"
    PULMONARY_FUNCTION = "pulmonary_function"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    EXPOSURE = "exposure"
    SMOKING_HISTORY = "smoking_history"
    FAMILY_HISTORY = "family_history"
    ALLERGY = "allergy"
    TREATMENT = "treatment"
    TREATMENT_RESPONSE = "treatment_response"
    FOLLOW_UP_FINDING = "follow_up_finding"
    MDT_STATEMENT = "mdt_statement"
    TEMPORAL_EVENT = "temporal_event"
    OTHER = "other"
    UNCERTAIN = "uncertain"


class ClinicalDomain(StrEnum):
    """Clinical domain for routing evidence atoms without judging diagnoses."""

    RESPIRATORY = "respiratory"
    RHEUMATOLOGY_IMMUNOLOGY = "rheumatology_immunology"
    RADIOLOGY = "radiology"
    PATHOLOGY = "pathology"
    LABORATORY = "laboratory"
    PULMONARY_FUNCTION = "pulmonary_function"
    TREATMENT = "treatment"
    EXPOSURE_ENVIRONMENT = "exposure_environment"
    CARDIOVASCULAR = "cardiovascular"
    INFECTIOUS_DISEASE = "infectious_disease"
    GENERAL = "general"
    OTHER = "other"
    UNCERTAIN = "uncertain"


class EvidenceGranularity(StrEnum):
    """How atomized this evidence unit is for downstream reasoning."""

    ATOMIC = "atomic"
    COMPOUND = "compound"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"
    UNCERTAIN = "uncertain"


class AtomizationTransformationType(StrEnum):
    """How a StructuredClinicalItem became EvidenceAtom material."""

    COPIED = "copied"
    SPLIT = "split"
    NORMALIZED = "normalized"
    MERGED = "merged"
    DEFERRED = "deferred"
    DROPPED = "dropped"


class DeferredReason(StrEnum):
    """Reason a StructuredClinicalItem was not safely atomized."""

    TOO_AMBIGUOUS = "too_ambiguous"
    NOT_CLINICAL_EVIDENCE = "not_clinical_evidence"
    INSUFFICIENT_SOURCE_SPAN = "insufficient_source_span"
    ADMINISTRATIVE_TEXT = "administrative_text"
    DUPLICATE_OF_EXISTING_ATOM = "duplicate_of_existing_atom"
    REQUIRES_DOWNSTREAM_INTERPRETATION = "requires_downstream_interpretation"
    OUTSIDE_ATOMIZER_SCOPE = "outside_atomizer_scope"


# ---------------------------------------------------------------------
# Boundary helpers
# ---------------------------------------------------------------------

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
            f"{field_name} must describe atomization quality only and must not "
            "include explicit downstream judgment or action patterns such as "
            "diagnosis/hypothesis support or refutation, diagnosis selection, "
            "treatment recommendation, conflict resolution, action plan, update "
            "decision, safety gate result, or arbitration result. "
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
