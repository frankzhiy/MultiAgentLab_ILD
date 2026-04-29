"""Structured clinical item schema for the Case Structurer.

StructuredClinicalItem represents a fine-grained clinical item extracted
from one ClinicalSection.

It answers one question:

    What specific clinical fact or statement appears inside this section?

StructuredClinicalItem is still part of case structuring. It must not
represent evidence atoms, diagnoses, hypotheses, conflicts, actions,
treatment recommendations, or arbitration results.

Reasoning evidence for downstream hypothesis management belongs to
EvidenceAtom, not StructuredClinicalItem.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.utils.id_generator import generate_item_id

from .common import (
    CertaintyLevel,
    ConfidenceLevel,
    InputID,
    ItemID,
    NegationStatus,
    SectionID,
    TemporalRelation,
)
from .source_span import SourceSpan


class ClinicalItemType(StrEnum):
    """Fine-grained clinical item type.

    This is more specific than ClinicalSectionType.

    ClinicalSectionType answers:
        What broad clinical block does this text belong to?

    ClinicalItemType answers:
        What specific kind of clinical fact is this item?

    This enum must not include diagnostic hypothesis categories such as
    IPF, CTD-ILD, fibrotic HP, infection, or acute exacerbation. Those
    belong to later hypothesis-level schemas, not Case Structurer schemas.
    """

    DEMOGRAPHIC = "demographic"

    SYMPTOM = "symptom"
    SIGN = "sign"

    DIAGNOSIS_HISTORY = "diagnosis_history"
    COMORBIDITY = "comorbidity"

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

    OTHER = "other"
    UNCERTAIN = "uncertain"


class StructuredClinicalItem(BaseModel):
    """A fine-grained clinical item extracted from one ClinicalSection.

    StructuredClinicalItem turns section-level text into concrete clinical
    facts or statements such as symptoms, lab results, medications,
    exposures, imaging findings, pathology findings, or treatment response.

    It does not answer:

    - What diagnosis is likely?
    - What hypothesis does this item support or refute?
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

    item_id: ItemID = Field(
        default_factory=generate_item_id,
        description="Unique id for this structured clinical item.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this clinical item was extracted from.",
    )

    section_id: SectionID = Field(
        ...,
        description=(
            "ClinicalSection id that this item belongs to. "
            "The item references the section by id to avoid deep nested imports."
        ),
    )

    item_type: ClinicalItemType = Field(
        ...,
        description=(
            "Fine-grained clinical item type, such as symptom, lab_result, "
            "imaging_finding, medication, exposure, or treatment_response."
        ),
    )

    label: str = Field(
        ...,
        min_length=1,
        description=(
            "Normalized or source-level name of the clinical item, such as "
            "'cough', 'dyspnea', 'ANA', 'hypertension', 'prednisone', "
            "'honeycombing', 'FVC', or 'DLCO'."
        ),
    )

    value: str | None = Field(
        default=None,
        description=(
            "Optional value of the item, such as 'positive', '77', '8 years', "
            "'elevated', 'decreased', or 'present'. Use None if no explicit "
            "value is available."
        ),
    )

    unit: str | None = Field(
        default=None,
        description=(
            "Optional measurement unit, such as 'years', 'mg/L', 'mmHg', '%', "
            "'L', or 'mg/day'. Use None when not applicable."
        ),
    )

    body_site: str | None = Field(
        default=None,
        description=(
            "Optional anatomical site or organ location, such as 'lung', "
            "'bilateral lungs', 'left lower lobe', or 'lower limb'."
        ),
    )

    temporality: TemporalRelation = Field(
        default=TemporalRelation.UNKNOWN,
        description=(
            "Broad temporal status of this clinical item, such as current, "
            "past, chronic, recent_worsening, follow_up, or unknown."
        ),
    )

    time_text: str | None = Field(
        default=None,
        description=(
            "Optional time expression as written in the source text, such as "
            "'8年', '2月', '40年前', '近期', or '入院前'. This field preserves "
            "the source-level expression and does not require normalized time."
        ),
    )

    certainty: CertaintyLevel = Field(
        default=CertaintyLevel.UNKNOWN,
        description=(
            "Certainty of this clinical statement as expressed in the source "
            "text, not diagnostic certainty."
        ),
    )

    negation: NegationStatus = Field(
        default=NegationStatus.UNKNOWN,
        description=(
            "Whether this clinical item is present, absent, denied, not "
            "mentioned, or unknown."
        ),
    )

    source_spans: list[SourceSpan] = Field(
        ...,
        min_length=1,
        description=(
            "Source spans showing where this clinical item came from in the "
            "original RawTextInput. At least one span is required for provenance."
        ),
    )

    item_order: int = Field(
        ...,
        ge=1,
        description=(
            "Order of this item within the same RawTextInput. This is text "
            "order, not necessarily clinical event time."
        ),
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence in item_type and item boundary classification. "
            "This is extraction confidence, not diagnostic confidence."
        ),
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional non-diagnostic note about item extraction or classification. "
            "Must not include diagnosis, hypothesis, evidence polarity, treatment "
            "recommendation, conflict, action, or arbitration result."
        ),
    )

    @field_validator(
        "label",
        mode="after",
    )
    @classmethod
    def label_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only labels."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("label must not be empty.")
        return cleaned

    @field_validator(
        "value",
        "unit",
        "body_site",
        "time_text",
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

    @model_validator(mode="after")
    def validate_source_span_input_consistency(self) -> "StructuredClinicalItem":
        """Validate that all source spans come from the same RawTextInput.

        A StructuredClinicalItem belongs to one RawTextInput. Therefore,
        every SourceSpan attached to this item must have the same input_id.
        """
        mismatched_span_ids = [
            span.span_id
            for span in self.source_spans
            if span.input_id != self.input_id
        ]

        if mismatched_span_ids:
            raise ValueError(
                "All source_spans must have the same input_id as the "
                f"StructuredClinicalItem. Mismatched span ids: {mismatched_span_ids}"
            )

        return self