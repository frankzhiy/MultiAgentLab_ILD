from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.common import ConfidenceLevel
from src.utils.id_generator import generate_id

from .atomization_warning import AtomizationWarning
from .common import ItemID, SpanID, normalize_optional_text, require_non_empty_text


class ClinicalObjectType(StrEnum):
    SYMPTOM = "symptom"
    SIGN = "sign"
    FINDING = "finding"
    LAB_OR_TEST = "lab_or_test"
    IMAGING_FINDING = "imaging_finding"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    TREATMENT = "treatment"
    TREATMENT_RESPONSE = "treatment_response"
    ETIOLOGY_OR_TRIGGER = "etiology_or_trigger"
    CARE_SEEKING_OR_MANAGEMENT = "care_seeking_or_management"
    OTHER = "other"
    UNCERTAIN = "uncertain"


class ClinicalObjectAssertionStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    POSSIBLE = "possible"
    UNCERTAIN = "uncertain"


class ClinicalObjectAssertion(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    object_id: str = Field(
        default_factory=lambda: generate_id("clinical_object_assertion")
    )
    source_item_id: ItemID

    object_text: str
    object_type: ClinicalObjectType

    assertion_status: ClinicalObjectAssertionStatus
    assertion_cue_text: str | None = None
    assertion_scope_text: str | None = None

    context_text: str
    source_span_ids: list[SpanID] = Field(default_factory=list)

    confidence: ConfidenceLevel
    notes: str | None = None

    @field_validator("object_text", "context_text", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "Required text fields")

    @field_validator(
        "assertion_cue_text",
        "assertion_scope_text",
        "notes",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)


class ClinicalAssertionResolutionResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    clinical_object_assertions: list[ClinicalObjectAssertion] = Field(
        default_factory=list
    )
    assertion_warnings: list[AtomizationWarning] = Field(default_factory=list)