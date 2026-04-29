"""Timeline event schema for the Case Structurer.

TimelineEvent represents a time-related clinical event extracted from one
RawTextInput.

It answers one question:

    When did a clinical event happen in the case trajectory?

TimelineEvent is still part of case structuring. It must not represent
evidence atoms, diagnoses, hypotheses, conflicts, actions, treatment
recommendations, or arbitration results.

Reasoning evidence for downstream hypothesis management belongs to
EvidenceAtom, not TimelineEvent.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.utils.id_generator import generate_event_id

from .common import (
    ConfidenceLevel,
    EventID,
    InputID,
    ItemID,
    TimeExpressionType,
)
from .source_span import SourceSpan


class TimelineEventType(StrEnum):
    """Broad type of clinical event in the case trajectory.

    This enum describes the event type, not its diagnostic interpretation.

    For example, DIAGNOSIS_MADE means the source text states that a
    diagnosis was made or considered somewhere in the clinical history.
    It does not mean the Case Structurer is making a diagnosis.
    """

    SYMPTOM_ONSET = "symptom_onset"
    SYMPTOM_WORSENING = "symptom_worsening"
    SYMPTOM_IMPROVEMENT = "symptom_improvement"

    DIAGNOSIS_MADE = "diagnosis_made"

    TEST_PERFORMED = "test_performed"
    TEST_RESULT_AVAILABLE = "test_result_available"

    TREATMENT_STARTED = "treatment_started"
    TREATMENT_CHANGED = "treatment_changed"
    TREATMENT_RESPONSE = "treatment_response"

    PROCEDURE_PERFORMED = "procedure_performed"
    HOSPITALIZATION = "hospitalization"
    FOLLOW_UP = "follow_up"
    MDT_DISCUSSION = "mdt_discussion"

    OTHER = "other"
    UNKNOWN = "unknown"


class TimelineEvent(BaseModel):
    """A time-related clinical event extracted from one RawTextInput.

    TimelineEvent turns temporally relevant clinical information into
    case-trajectory events such as symptom onset, symptom worsening,
    test completion, treatment start, treatment response, follow-up, or
    MDT discussion.

    It does not answer:

    - What diagnosis is likely?
    - What hypothesis does this event support or refute?
    - What evidence atom should be created?
    - What treatment should be recommended?
    - What conflict exists?
    - What action should be taken?

    Those responsibilities belong to later schemas and agents.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    event_id: EventID = Field(
        default_factory=generate_event_id,
        description="Unique id for this timeline event.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this timeline event was extracted from.",
    )

    event_type: TimelineEventType = Field(
        ...,
        description=(
            "Broad type of this clinical event, such as symptom onset, "
            "symptom worsening, test performed, treatment started, or follow-up."
        ),
    )

    event_time_text: str | None = Field(
        default=None,
        description=(
            "Original time expression from the source text, such as '8年', "
            "'2月', '40年前', '入院前', '近1周', or '2024年5月'. "
            "Use None when no explicit time expression is available."
        ),
    )

    time_expression_type: TimeExpressionType = Field(
        default=TimeExpressionType.UNKNOWN,
        description=(
            "Type of time expression, such as absolute, relative, duration, "
            "frequency, approximate, or unknown."
        ),
    )

    normalized_time: str | None = Field(
        default=None,
        description=(
            "Optional normalized time if it can be reliably inferred. "
            "Use None when normalization would require guessing."
        ),
    )

    relative_time: str | None = Field(
        default=None,
        description=(
            "Optional normalized relative time expression, such as "
            "'8 years ago', '2 months ago', or '40 years ago'. "
            "Use None when unavailable or unreliable."
        ),
    )

    description: str = Field(
        ...,
        min_length=1,
        description=(
            "Non-diagnostic description of the event. This should describe "
            "what happened without adding diagnostic interpretation."
        ),
    )

    related_item_ids: list[ItemID] = Field(
        default_factory=list,
        description=(
            "StructuredClinicalItem ids related to this event. "
            "Use ids instead of embedding StructuredClinicalItem objects to "
            "avoid deep nested schema dependencies."
        ),
    )

    source_spans: list[SourceSpan] = Field(
        ...,
        min_length=1,
        description=(
            "Source spans showing where this timeline event came from in the "
            "original RawTextInput. At least one span is required for provenance."
        ),
    )

    event_order: int = Field(
        ...,
        ge=1,
        description=(
            "Order of this event in the reconstructed case timeline. "
            "This is clinical timeline order, not necessarily text order."
        ),
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence in event_type, event boundary, and time interpretation. "
            "This is extraction confidence, not diagnostic confidence."
        ),
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional non-diagnostic note about event extraction or time "
            "interpretation. Must not include diagnosis, hypothesis, evidence "
            "polarity, treatment recommendation, conflict, action, or arbitration result."
        ),
    )

    @field_validator(
        "event_time_text",
        "normalized_time",
        "relative_time",
        "notes",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize optional text fields.

        Blank strings are converted to None to avoid meaningless metadata.
        """
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        return cleaned

    @field_validator("description", mode="after")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only descriptions."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("description must not be empty.")
        return cleaned

    @model_validator(mode="after")
    def validate_source_span_input_consistency(self) -> "TimelineEvent":
        """Validate that all source spans come from the same RawTextInput.

        A TimelineEvent belongs to one RawTextInput. Therefore, every
        SourceSpan attached to this event must have the same input_id.
        """
        mismatched_span_ids = [
            span.span_id
            for span in self.source_spans
            if span.input_id != self.input_id
        ]

        if mismatched_span_ids:
            raise ValueError(
                "All source_spans must have the same input_id as the "
                f"TimelineEvent. Mismatched span ids: {mismatched_span_ids}"
            )

        return self

    @model_validator(mode="after")
    def validate_time_expression_consistency(self) -> "TimelineEvent":
        """Validate consistency between time text and time expression type.

        If no explicit event_time_text is available, the time expression type
        should remain UNKNOWN. This prevents the model from claiming a
        relative, absolute, duration, frequency, or approximate time expression
        without a source-level time phrase.
        """
        if self.event_time_text is None and self.time_expression_type != TimeExpressionType.UNKNOWN:
            raise ValueError(
                "time_expression_type must be unknown when event_time_text is None."
            )

        return self