"""Stage context schema for the Case Structurer.

StageContext describes where one RawTextInput fits in a case trajectory.

It combines:
1. system-determined fields, such as case_id, input_id, stage_order;
2. LLM-inferred workflow classification fields, such as stage_type and
   relation_to_previous_stage;
3. validation rules that prevent internally inconsistent stage metadata.

This schema must not extract clinical findings, diagnoses, hypotheses,
evidence atoms, conflicts, actions, treatment recommendations, or
arbitration results.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import CaseID, ConfidenceLevel, InputID, StageID


def _utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _new_stage_id() -> StageID:
    """Generate a stable stage id."""
    return f"stage_{uuid4().hex}"


class StageType(StrEnum):
    """Broad workflow type of this input within the case trajectory.

    This is a coarse classification of the input's role, not a detailed
    clinical content category.

    Detailed clinical categories such as symptoms, imaging, pathology,
    laboratory tests, and treatment response belong to ClinicalSection and
    StructuredClinicalItem, not StageContext.
    """

    INITIAL_INPUT = "initial_input"
    SUPPLEMENTARY_INPUT = "supplementary_input"
    NEW_TEST_RESULT = "new_test_result"
    FOLLOW_UP_INPUT = "follow_up_input"
    MDT_DISCUSSION_INPUT = "mdt_discussion_input"
    TREATMENT_UPDATE = "treatment_update"
    UNKNOWN = "unknown"


class StageRelation(StrEnum):
    """How this input relates to the previous known case state.

    This relation is usually inferred from text content and prior case
    state. It should be treated as a workflow-level classification, not
    as a clinical diagnosis or evidence judgment.
    """

    NEW_CASE_START = "new_case_start"
    ADDS_INFORMATION = "adds_information"
    UPDATES_PRIOR_INFORMATION = "updates_prior_information"
    CORRECTS_PRIOR_INFORMATION = "corrects_prior_information"
    SUMMARIZES_PRIOR_INFORMATION = "summarizes_prior_information"
    UNKNOWN = "unknown"


class StageContext(BaseModel):
    """Workflow context for one RawTextInput.

    StageContext answers:

    - Which case does this input belong to?
    - Which stage of the case trajectory is this?
    - Is this the first input or a later input?
    - What broad type of input does it appear to be?
    - How does it relate to previous case information?

    It does not answer:

    - What symptoms or findings are present?
    - What diagnosis is likely?
    - What evidence supports or refutes a disease?
    - What treatment should be recommended?

    System code should determine identity/order fields whenever possible.
    The LLM should only infer semantic workflow classification fields such
    as stage_type, relation_to_previous_stage, classification_confidence,
    and classification_basis.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    stage_id: StageID = Field(
        default_factory=_new_stage_id,
        description="Unique id for this case stage.",
    )

    case_id: CaseID = Field(
        ...,
        description="Case id this stage belongs to.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this StageContext describes.",
    )

    stage_order: int = Field(
        ...,
        ge=1,
        description=(
            "Order of this stage within the same case trajectory. "
            "This is workflow order, not necessarily clinical event time."
        ),
    )

    stage_type: StageType = Field(
        default=StageType.UNKNOWN,
        description=(
            "Broad workflow type of this input. This is inferred from text "
            "content and case context when not system-determined."
        ),
    )

    relation_to_previous_stage: StageRelation = Field(
        default=StageRelation.UNKNOWN,
        description="How this stage relates to the previous known case state.",
    )

    previous_stage_id: StageID | None = Field(
        default=None,
        description=(
            "Previous stage id if this stage follows an earlier stage in the "
            "same case. Must be None for the initial stage."
        ),
    )

    is_initial_stage: bool = Field(
        default=False,
        description="Whether this is the first structured stage of the case.",
    )

    created_at: datetime = Field(
        default_factory=_utc_now,
        description="Timezone-aware timestamp when this StageContext was created.",
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence in stage_type and relation_to_previous_stage. "
            "This is workflow classification confidence, not diagnostic confidence."
        ),
    )

    classification_basis: str | None = Field(
        default=None,
        description=(
            "Brief explanation of why this stage_type and relation were assigned. "
            "Must not contain diagnosis, hypothesis, evidence interpretation, "
            "or treatment recommendation."
        ),
    )

    @field_validator("classification_basis")
    @classmethod
    def classification_basis_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize optional classification basis."""
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        return cleaned

    @model_validator(mode="after")
    def validate_initial_stage_consistency(self) -> "StageContext":
        """Validate internal consistency for initial and non-initial stages.

        Rules:
        - Initial stage must be stage_order == 1.
        - Initial stage must not have previous_stage_id.
        - Initial stage must have relation_to_previous_stage == new_case_start.
        - stage_order == 1 must be marked as is_initial_stage.
        - Non-initial stage must not use relation new_case_start.
        """
        if self.is_initial_stage:
            if self.stage_order != 1:
                raise ValueError("Initial stage must have stage_order == 1.")

            if self.previous_stage_id is not None:
                raise ValueError("Initial stage must not have previous_stage_id.")

            if self.relation_to_previous_stage != StageRelation.NEW_CASE_START:
                raise ValueError(
                    "Initial stage must have "
                    "relation_to_previous_stage == new_case_start."
                )

        if self.stage_order == 1 and not self.is_initial_stage:
            raise ValueError("stage_order == 1 must be marked as is_initial_stage=True.")

        if not self.is_initial_stage:
            if self.relation_to_previous_stage == StageRelation.NEW_CASE_START:
                raise ValueError(
                    "Non-initial stage must not have "
                    "relation_to_previous_stage == new_case_start."
                )

        return self

    @model_validator(mode="after")
    def validate_initial_stage_type(self) -> "StageContext":
        """Validate broad consistency between initial flag and stage_type.

        The first input should normally be INITIAL_INPUT or UNKNOWN.
        UNKNOWN is allowed because a very short first input may not provide
        enough semantic context for confident classification.
        """
        if self.is_initial_stage and self.stage_type not in {
            StageType.INITIAL_INPUT,
            StageType.UNKNOWN,
        }:
            raise ValueError(
                "Initial stage should have stage_type == initial_input or unknown."
            )

        return self