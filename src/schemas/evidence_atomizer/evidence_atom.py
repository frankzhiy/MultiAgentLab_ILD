"""Evidence atom schema for the Evidence Atomizer.

EvidenceAtom is the smallest source-grounded clinical evidence unit that
downstream hypothesis, conflict, update, and arbitration modules can
reference.

It is different from StructuredClinicalItem:
- StructuredClinicalItem says what clinical fact appears in the structured case.
- EvidenceAtom is a minimal evidence unit for downstream reasoning.
- EvidenceAtom does not decide what diagnosis it supports or refutes.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.schemas.attribute_extractor.common import AttributeID
from src.utils.id_generator import generate_evidence_id

from .common import (
    CaseID,
    CertaintyLevel,
    ClinicalDomain,
    ConfidenceLevel,
    EvidenceGranularity,
    EvidenceID,
    EvidenceType,
    InputID,
    ItemID,
    NegationStatus,
    SpanID,
    StageID,
    TemporalRelation,
    normalize_optional_text,
    reject_reasoning_scope_text,
    require_non_empty_text,
    validate_no_forbidden_schema_fields,
)


class EvidenceAtom(BaseModel):
    """A minimal source-grounded evidence unit for later reasoning phases.

    EvidenceAtom preserves the evidence material and provenance that later
    modules may reference. It does not generate diagnoses, hypothesis states,
    evidence polarity, treatment recommendations, conflict resolution, update
    traces, safety gate results, or arbitration outcomes.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    evidence_id: EvidenceID = Field(
        default_factory=generate_evidence_id,
        description="Unique id for this evidence atom.",
    )

    case_id: CaseID = Field(
        ...,
        description="Case id this evidence atom belongs to.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this evidence atom was derived from.",
    )

    stage_id: StageID | None = Field(
        default=None,
        description="Optional StageContext id associated with this evidence atom.",
    )

    evidence_type: EvidenceType = Field(
        ...,
        description="Source-level type of evidence without diagnostic interpretation.",
    )

    clinical_domain: ClinicalDomain = Field(
        ...,
        description="Clinical domain of the evidence atom.",
    )

    granularity: EvidenceGranularity = Field(
        ...,
        description="Granularity of this evidence unit.",
    )

    statement: str = Field(
        ...,
        min_length=1,
        description="Minimal normalized evidence statement grounded in source text.",
    )

    normalized_label: str | None = Field(
        default=None,
        description="Optional normalized label for this evidence atom.",
    )

    assertion_status: NegationStatus = Field(
        ...,
        description="Whether the evidence statement is present, absent, denied, or unknown.",
    )

    certainty: CertaintyLevel = Field(
        ...,
        description="Certainty of the statement as expressed in source text.",
    )

    temporality: TemporalRelation = Field(
        ...,
        description="Broad temporal relation of this evidence atom.",
    )

    source_item_ids: list[ItemID] = Field(
        ...,
        min_length=1,
        description="StructuredClinicalItem ids used to produce this atom.",
    )

    source_attribute_ids: list[AttributeID] = Field(
        default_factory=list,
        description="ClinicalAttribute ids used to produce this atom.",
    )

    source_span_ids: list[SpanID] = Field(
        ...,
        min_length=1,
        description="SourceSpan ids grounding this atom in the original text.",
    )

    source_text: str = Field(
        ...,
        min_length=1,
        description="Source text fragment grounding this atom.",
    )

    atomization_confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence in atom boundary and normalization, not diagnosis.",
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional note about atomization quality only. Must not contain "
            "diagnosis, hypothesis judgment, treatment recommendation, conflict, "
            "action, update, safety gate, or arbitration content."
        ),
    )

    @field_validator("statement", "source_text", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only required text fields."""
        return require_non_empty_text(value, "Required text fields")

    @field_validator(
        "normalized_label",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize blank optional text fields to None."""
        return normalize_optional_text(value)

    @field_validator("notes", mode="after")
    @classmethod
    def notes_must_stay_in_atomization_scope(cls, value: str | None) -> str | None:
        """Reject notes that cross into downstream reasoning."""
        return reject_reasoning_scope_text(value, "notes")

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "EvidenceAtom":
        """Validate that EvidenceAtom does not expose downstream fields."""
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
