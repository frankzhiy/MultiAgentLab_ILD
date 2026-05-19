"""EvidenceNode schema.

An EvidenceNode represents one source-grounded clinical object, temporal
context, cue, test, result, property, quantity, location, severity,
management event, treatment, or impression.

Composite source phrases that summarize multiple component facts must be
represented as an EvidenceFrame.frame_label, NOT as an EvidenceNode.

This schema intentionally does NOT include parent_node_id or
relation_to_parent. Inter-object structure lives in EvidenceRelation.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.common import ConfidenceLevel
from src.utils.id_generator import generate_id

from .clinical_object_assertion import ClinicalObjectAssertionStatus
from .common import ItemID, SpanID, normalize_optional_text, require_non_empty_text


class EvidenceNodeType(StrEnum):
    CLINICAL_OBJECT = "clinical_object"
    TEMPORAL_CONTEXT = "temporal_context"
    NEGATION_CUE = "negation_cue"
    CERTAINTY_CUE = "certainty_cue"
    TEST_NAME = "test_name"
    TEST_RESULT = "test_result"
    MANAGEMENT_EVENT = "management_event"
    TREATMENT_EVENT = "treatment_event"
    DIAGNOSTIC_IMPRESSION = "diagnostic_impression"
    OBJECT_PROPERTY = "object_property"
    QUANTITY = "quantity"
    LOCATION = "location"
    SEVERITY = "severity"
    UNCERTAIN_OTHER = "uncertain_other"


class EvidenceNode(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    node_id: str = Field(default_factory=lambda: generate_id("evidence_node"))
    source_item_id: ItemID

    node_type: EvidenceNodeType
    text: str = Field(
        ...,
        description="Source-grounded text for this node.",
    )

    assertion_ids: list[str] = Field(
        default_factory=list,
        description="ClinicalObjectAssertion ids this node represents or references.",
    )
    assertion_status: ClinicalObjectAssertionStatus | None = Field(
        default=None,
        description=(
            "Optional assertion status carried from the dominant underlying "
            "assertion. Not used as graph structure."
        ),
    )

    source_span_ids: list[SpanID] = Field(default_factory=list)

    confidence: ConfidenceLevel
    notes: str | None = None

    @field_validator("text", mode="after")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "text")

    @field_validator("notes", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator(
        "assertion_ids",
        "source_span_ids",
        mode="after",
    )
    @classmethod
    def normalize_id_list(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in value:
            normalized = normalize_optional_text(raw)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned
