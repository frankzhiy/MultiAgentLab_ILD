"""ClinicalObjectAssertion schema for the Evidence Tree Structurer.

This is the typed payload produced by the Clinical Assertion Resolver (LLM #1).
Each assertion describes one source-grounded clinical object plus its own
intrinsic context (assertion status, temporal anchor, trigger, modifiers).
Relationships *between* assertions (parent/child, relation type) are decided
by the Evidence Tree Builder (LLM #2); they are intentionally NOT carried on
the assertion itself.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.common import ConfidenceLevel
from src.utils.id_generator import generate_id

from .tree_structuring_warning import TreeStructuringWarning
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
    DEMOGRAPHIC = "demographic"
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

    temporal_anchor_text: str | None = Field(
        default=None,
        description=(
            "Source-copied time expression that scopes this assertion, "
            "for example '10天前' or '入院当日'."
        ),
    )
    trigger_text: str | None = Field(
        default=None,
        description=(
            "Source-copied trigger/cause phrase that precipitated this assertion, "
            "for example '受凉后' or '无明显诱因'."
        ),
    )
    modifier_texts: list[str] = Field(
        default_factory=list,
        description=(
            "Source-copied modifier phrases attached to this assertion, "
            "for example ['晨起', '活动后']."
        ),
    )

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
        "temporal_anchor_text",
        "trigger_text",
        "notes",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator("modifier_texts", mode="after")
    @classmethod
    def normalize_modifier_texts(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in value:
            normalized = normalize_optional_text(raw)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned

    @field_validator("source_span_ids", mode="after")
    @classmethod
    def normalize_span_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in value:
            normalized = normalize_optional_text(raw)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned


class ClinicalAssertionResolutionResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    clinical_object_assertions: list[ClinicalObjectAssertion] = Field(
        default_factory=list
    )
    assertion_warnings: list[TreeStructuringWarning] = Field(default_factory=list)
