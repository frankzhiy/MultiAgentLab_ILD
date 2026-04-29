"""Clinical section schema for the Case Structurer.

ClinicalSection represents a coarse clinical block extracted from one
RawTextInput.

It answers one question:

    What broad type of clinical information does this text span contain?

ClinicalSection is a section-level grouping object. It must not represent
evidence atoms, diagnoses, hypotheses, conflicts, actions, treatment
recommendations, or arbitration results.

Detailed clinical facts inside a section belong to StructuredClinicalItem.
Reasoning evidence for downstream hypothesis management belongs to
EvidenceAtom, not ClinicalSection.
"""

from __future__ import annotations

from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import ConfidenceLevel, InputID, SectionID
from .source_span import SourceSpan


def _new_section_id() -> SectionID:
    """Generate a stable clinical section id."""
    return f"section_{uuid4().hex}"


class ClinicalSectionType(StrEnum):
    """Coarse clinical section type within one raw text input.

    This is a broad clinical-document category, not a fine-grained
    evidence type and not a diagnostic category.

    Fine-grained clinical facts such as symptoms, lab values, imaging
    findings, medications, and exposures belong to StructuredClinicalItem.
    """

    DEMOGRAPHICS = "demographics"
    CHIEF_COMPLAINT = "chief_complaint"
    HISTORY_OF_PRESENT_ILLNESS = "history_of_present_illness"
    PAST_MEDICAL_HISTORY = "past_medical_history"
    MEDICATION_HISTORY = "medication_history"
    ALLERGY_HISTORY = "allergy_history"
    FAMILY_HISTORY = "family_history"
    EXPOSURE_HISTORY = "exposure_history"
    SMOKING_HISTORY = "smoking_history"
    PHYSICAL_EXAM = "physical_exam"

    LABORATORY_TEST = "laboratory_test"
    IMAGING = "imaging"
    PATHOLOGY = "pathology"
    PULMONARY_FUNCTION_TEST = "pulmonary_function_test"

    TREATMENT_HISTORY = "treatment_history"
    TREATMENT_RESPONSE = "treatment_response"
    FOLLOW_UP = "follow_up"
    MDT_OPINION = "mdt_opinion"

    OTHER = "other"
    UNCERTAIN = "uncertain"


class ClinicalSection(BaseModel):
    """A coarse clinical block extracted from one RawTextInput.

    ClinicalSection groups one or more source spans into a broad clinical
    category such as chief complaint, past history, imaging, laboratory
    tests, or treatment history.

    It does not extract individual clinical facts. It only provides a
    stable section boundary for later StructuredClinicalItem extraction.

    It does not answer:

    - What diagnosis is likely?
    - What hypothesis does this support or refute?
    - What treatment should be recommended?
    - What conflict exists?
    - What evidence atom should be created?

    Those responsibilities belong to later schemas and agents.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    section_id: SectionID = Field(
        default_factory=_new_section_id,
        description="Unique id for this clinical section.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this clinical section was extracted from.",
    )

    section_type: ClinicalSectionType = Field(
        ...,
        description=(
            "Broad clinical category of this section. This is a coarse "
            "document-level classification, not a diagnostic interpretation."
        ),
    )

    title: str | None = Field(
        default=None,
        description=(
            "Optional original or normalized heading for this section, such as "
            "'主诉', '现病史', '既往史', '辅助检查'. Use None if no heading exists."
        ),
    )

    normalized_text: str = Field(
        ...,
        min_length=1,
        description=(
            "Cleaned section text. This should preserve the clinical content "
            "without adding diagnostic interpretation or treatment recommendation."
        ),
    )

    source_spans: list[SourceSpan] = Field(
        ...,
        min_length=1,
        description=(
            "Source spans showing where this section came from in the original "
            "RawTextInput. At least one span is required for provenance."
        ),
    )

    section_order: int = Field(
        ...,
        ge=1,
        description=(
            "Order of this section within the same RawTextInput. This is text "
            "order, not necessarily clinical event time."
        ),
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence in the section_type classification. This is extraction "
            "confidence, not diagnostic confidence."
        ),
    )

    parent_section_id: SectionID | None = Field(
        default=None,
        description=(
            "Optional parent section id for simple hierarchical sections. "
            "For example, 'auxiliary tests' may contain laboratory, imaging, "
            "and pulmonary function subsections. Use None for top-level sections."
        ),
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional non-diagnostic note about section classification. "
            "Must not include diagnosis, hypothesis, evidence polarity, "
            "or treatment recommendation."
        ),
    )

    @field_validator("title", "notes")
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

    @field_validator("normalized_text")
    @classmethod
    def normalized_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only normalized section text."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("normalized_text must not be empty.")
        return cleaned

    @model_validator(mode="after")
    def validate_source_span_input_consistency(self) -> "ClinicalSection":
        """Validate that all source spans come from the same RawTextInput.

        A ClinicalSection belongs to one RawTextInput. Therefore, every
        SourceSpan attached to this section must have the same input_id.
        """
        mismatched_span_ids = [
            span.span_id
            for span in self.source_spans
            if span.input_id != self.input_id
        ]

        if mismatched_span_ids:
            raise ValueError(
                "All source_spans must have the same input_id as the "
                f"ClinicalSection. Mismatched span ids: {mismatched_span_ids}"
            )

        return self

    @model_validator(mode="after")
    def validate_parent_section_not_self(self) -> "ClinicalSection":
        """Prevent a section from being its own parent."""
        if self.parent_section_id is not None and self.parent_section_id == self.section_id:
            raise ValueError("parent_section_id must not equal section_id.")

        return self