"""Ambiguity item schema for the Case Structurer.

AmbiguityItem represents an uncertain, ambiguous, conflicting, or
under-specified statement found during case structuring.

It answers one question:

    What source-level statement should not be forced into a definite
    structured interpretation?

AmbiguityItem is still part of case structuring. It must not represent
evidence atoms, diagnoses, hypotheses, conflicts, actions, treatment
recommendations, or arbitration results.

Its purpose is to preserve uncertainty and prevent the Case Structurer
from hallucinating a definite interpretation where the source text does
not support one.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.utils.id_generator import generate_ambiguity_id

from .common import (
    AmbiguityID,
    ConfidenceLevel,
    InputID,
    ItemID,
    SectionID,
)
from .source_span import SourceSpan


class AmbiguityType(StrEnum):
    """Type of ambiguity or uncertainty in the source text.

    These types describe text-level or structuring-level uncertainty.
    They are not diagnostic categories and must not be used to encode
    hypothesis-level uncertainty.
    """

    UNCLEAR_TIME = "unclear_time"
    UNCLEAR_SUBJECT = "unclear_subject"
    UNCLEAR_NEGATION = "unclear_negation"
    UNCLEAR_CERTAINTY = "unclear_certainty"

    UNCLEAR_DIAGNOSIS_STATUS = "unclear_diagnosis_status"
    UNCLEAR_TEST_RESULT = "unclear_test_result"
    UNCLEAR_TREATMENT_STATUS = "unclear_treatment_status"
    UNCLEAR_RELATION_TO_PREVIOUS_STAGE = "unclear_relation_to_previous_stage"

    CONFLICTING_STATEMENT = "conflicting_statement"
    INSUFFICIENT_CONTEXT = "insufficient_context"

    OTHER = "other"


class AmbiguityItem(BaseModel):
    """An ambiguous or under-specified statement found during structuring.

    AmbiguityItem records text that the Case Structurer cannot safely
    convert into a single definite structured interpretation.

    It does not answer:

    - Which interpretation is clinically correct?
    - What diagnosis is likely?
    - What hypothesis does this support or refute?
    - What evidence atom should be created?
    - What treatment should be recommended?
    - What conflict exists at the hypothesis or management level?
    - What action should be taken?

    Those responsibilities belong to later schemas and agents.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    ambiguity_id: AmbiguityID = Field(
        default_factory=generate_ambiguity_id,
        description="Unique id for this ambiguity item.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this ambiguity was extracted from.",
    )

    ambiguity_type: AmbiguityType = Field(
        ...,
        description=(
            "Type of ambiguity, such as unclear time, unclear negation, "
            "unclear diagnosis status, conflicting statement, or insufficient context."
        ),
    )

    ambiguous_text: str = Field(
        ...,
        min_length=1,
        description="Original or near-original text fragment that is ambiguous.",
    )

    possible_interpretations: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Possible source-level interpretations. These are not final decisions. "
            "They should describe plausible readings of the text without choosing one."
        ),
    )

    reason: str = Field(
        ...,
        min_length=1,
        description=(
            "Brief explanation of why this text should not be forced into a "
            "single definite structured interpretation."
        ),
    )

    related_section_ids: list[SectionID] = Field(
        default_factory=list,
        description=(
            "Optional ClinicalSection ids related to this ambiguity. "
            "Use ids instead of embedding ClinicalSection objects to avoid deep nesting."
        ),
    )

    related_item_ids: list[ItemID] = Field(
        default_factory=list,
        description=(
            "Optional StructuredClinicalItem ids related to this ambiguity. "
            "Use ids instead of embedding StructuredClinicalItem objects to avoid deep nesting."
        ),
    )

    source_spans: list[SourceSpan] = Field(
        ...,
        min_length=1,
        description=(
            "Source spans showing where this ambiguity came from in the original "
            "RawTextInput. At least one span is required for provenance."
        ),
    )

    needs_clarification: bool = Field(
        default=False,
        description=(
            "Whether this ambiguity should be clarified by the user, clinician, "
            "or later workflow before being used for downstream reasoning."
        ),
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence that this text is genuinely ambiguous or unsafe to "
            "force into a definite structured interpretation. This is extraction "
            "confidence, not diagnostic confidence."
        ),
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional non-diagnostic note about ambiguity extraction. Must not "
            "include diagnosis, hypothesis, evidence polarity, treatment "
            "recommendation, conflict resolution, action, or arbitration result."
        ),
    )

    @field_validator("ambiguous_text", "reason", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only required text fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required text fields must not be empty.")
        return cleaned

    @field_validator("possible_interpretations", mode="after")
    @classmethod
    def possible_interpretations_must_not_contain_blank(
        cls,
        value: list[str],
    ) -> list[str]:
        """Reject blank possible interpretations."""
        cleaned_items: list[str] = []

        for item in value:
            cleaned = item.strip()
            if not cleaned:
                raise ValueError("possible_interpretations must not contain blank items.")
            cleaned_items.append(cleaned)

        return cleaned_items

    @field_validator("notes", mode="after")
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

    @model_validator(mode="after")
    def validate_source_span_input_consistency(self) -> "AmbiguityItem":
        """Validate that all source spans come from the same RawTextInput.

        An AmbiguityItem belongs to one RawTextInput. Therefore, every
        SourceSpan attached to this ambiguity must have the same input_id.
        """
        mismatched_span_ids = [
            span.span_id
            for span in self.source_spans
            if span.input_id != self.input_id
        ]

        if mismatched_span_ids:
            raise ValueError(
                "All source_spans must have the same input_id as the "
                f"AmbiguityItem. Mismatched span ids: {mismatched_span_ids}"
            )

        return self

    @model_validator(mode="after")
    def validate_conflicting_statement_has_enough_context(self) -> "AmbiguityItem":
        """Light validation for conflicting statements.

        A conflicting statement often comes from multiple source spans, but
        copied clinical text can compress the conflict into one sentence.
        Therefore, this validator does not require at least two spans.

        It only requires that conflicting statements provide at least two
        possible interpretations, so the ambiguity is explicit.
        """
        if (
            self.ambiguity_type == AmbiguityType.CONFLICTING_STATEMENT
            and len(self.possible_interpretations) < 2
        ):
            raise ValueError(
                "conflicting_statement ambiguity should provide at least two "
                "possible_interpretations."
            )

        return self