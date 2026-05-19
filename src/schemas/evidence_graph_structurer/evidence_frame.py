"""EvidenceFrame schema.

An EvidenceFrame is a semantic container that groups assertions and evidence
nodes that belong to the same source-grounded clinical scene (a symptom
course, a lab panel, a care-seeking event, etc.).

The frame_label is a human-readable label only. It is NOT an EvidenceNode and
must not be treated as one.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.common import ConfidenceLevel
from src.utils.id_generator import generate_id

from .common import ItemID, SpanID, normalize_optional_text, require_non_empty_text


class EvidenceFrameType(StrEnum):
    SYMPTOM_COURSE = "symptom_course"
    CARE_SEEKING = "care_seeking"
    NEGATED_SYMPTOM_GROUP = "negated_symptom_group"
    LAB_PANEL = "lab_panel"
    TEST_RESULT_GROUP = "test_result_group"
    TREATMENT_EXPOSURE = "treatment_exposure"
    TREATMENT_RESPONSE = "treatment_response"
    DIAGNOSTIC_IMPRESSION = "diagnostic_impression"
    PAST_HISTORY = "past_history"
    EXPOSURE_HISTORY = "exposure_history"
    PHYSICAL_EXAM = "physical_exam"
    DISEASE_STATUS = "disease_status"
    PROCEDURE_OR_INTERVENTION = "procedure_or_intervention"
    FOLLOW_UP_OR_REASSESSMENT = "follow_up_or_reassessment"
    UNCERTAIN_OTHER = "uncertain_other"


class EvidenceFrame(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    frame_id: str = Field(default_factory=lambda: generate_id("evidence_frame"))
    source_item_id: ItemID

    frame_type: EvidenceFrameType
    frame_label: str = Field(
        ...,
        description=(
            "Human-readable label for this frame. Allowed to summarize a "
            "composite source phrase, but is NOT an EvidenceNode."
        ),
    )

    member_assertion_ids: list[str] = Field(default_factory=list)
    member_node_ids: list[str] = Field(default_factory=list)

    source_span_ids: list[SpanID] = Field(default_factory=list)

    confidence: ConfidenceLevel
    notes: str | None = None

    @field_validator("frame_label", mode="after")
    @classmethod
    def label_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "frame_label")

    @field_validator("notes", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator(
        "member_assertion_ids",
        "member_node_ids",
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
