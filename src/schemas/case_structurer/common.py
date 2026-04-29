"""Shared primitive types and enums for Case Structurer schemas.

This module only contains reusable primitive aliases and enums.
It must not contain Pydantic models, agent logic, validators, mock data,
or phase-specific schemas such as EvidenceAtom, HypothesisState, Conflict,
UpdateTrace, ActionPlan, or ArbitrationResult.
"""

from enum import StrEnum
from typing import TypeAlias


# ---------------------------------------------------------------------
# ID aliases
# ---------------------------------------------------------------------

CaseID: TypeAlias = str
StageID: TypeAlias = str
InputID: TypeAlias = str
SectionID: TypeAlias = str
ItemID: TypeAlias = str
EventID: TypeAlias = str
AmbiguityID: TypeAlias = str
SpanID: TypeAlias = str


# ---------------------------------------------------------------------
# General confidence / certainty / negation
# ---------------------------------------------------------------------

class ConfidenceLevel(StrEnum):
    """Confidence of the system extraction or classification.

    This is about how confident the Case Structurer is in its own
    structuring decision, not diagnostic confidence.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CertaintyLevel(StrEnum):
    """Certainty of the clinical statement as expressed in the source text."""

    DEFINITE = "definite"
    PROBABLE = "probable"
    POSSIBLE = "possible"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class NegationStatus(StrEnum):
    """Whether a clinical item is affirmed, denied, absent, or not stated."""

    PRESENT = "present"
    ABSENT = "absent"
    DENIED = "denied"
    NOT_MENTIONED = "not_mentioned"
    UNKNOWN = "unknown"



# ---------------------------------------------------------------------
# Temporal attributes
# ---------------------------------------------------------------------

class TemporalRelation(StrEnum):
    """Broad temporal status of a clinical item.

    This is not a full temporal reasoning graph. It only gives the
    Case Structurer enough vocabulary to distinguish current, past,
    chronic, recent worsening, and follow-up information.
    """

    CURRENT = "current"
    PAST = "past"
    CHRONIC = "chronic"
    RECENT_WORSENING = "recent_worsening"
    FOLLOW_UP = "follow_up"
    UNKNOWN = "unknown"


class TimeExpressionType(StrEnum):
    """Type of time expression found in the clinical text."""

    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    DURATION = "duration"
    FREQUENCY = "frequency"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------
# Validation severity
# ---------------------------------------------------------------------

class ValidationSeverity(StrEnum):
    """Severity level for structuring warnings or validation messages."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"