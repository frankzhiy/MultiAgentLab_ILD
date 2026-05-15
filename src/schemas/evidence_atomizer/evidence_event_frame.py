"""EvidenceEventFrame schema for frame-guided evidence atomization."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.utils.id_generator import (
    generate_evidence_frame_id,
    generate_evidence_frame_node_id,
)

from .atomization_warning import AtomizationWarning
from .common import (
    CertaintyLevel,
    ConfidenceLevel,
    ItemID,
    NegationStatus,
    SpanID,
    TemporalRelation,
    normalize_optional_text,
    require_non_empty_text,
    validate_no_forbidden_schema_fields,
)


class FrameNodeType(StrEnum):
    TEMPORAL_CONTEXT = "temporal_context"
    TRIGGER_OR_BACKGROUND_CONTEXT = "trigger_or_background_context"
    MAIN_EVENT = "main_event"
    CLINICAL_OBJECT = "clinical_object"
    OBJECT_PROPERTY = "object_property"
    SYMPTOM_MODIFIER = "symptom_modifier"
    NEGATIVE_FINDING = "negative_finding"
    MANAGEMENT_EVENT = "management_event"
    TREATMENT_EVENT = "treatment_event"
    TREATMENT_RESPONSE = "treatment_response"
    TEST_OR_MEASUREMENT = "test_or_measurement"
    RESULT_MODIFIER = "result_modifier"
    UNCERTAIN_OR_OTHER = "uncertain_or_other"


class FrameRelationType(StrEnum):
    ROOT_OF = "root_of"
    TEMPORAL_CONTEXT_OF = "temporal_context_of"
    BACKGROUND_CONTEXT_OF = "background_context_of"
    TRIGGER_CONTEXT_OF = "trigger_context_of"
    OCCURRENCE_OF = "occurrence_of"
    ASSOCIATED_WITH = "associated_with"
    PROPERTY_OF = "property_of"
    MODIFIER_OF = "modifier_of"
    NEGATIVE_CONTRAST_OF = "negative_contrast_of"
    MANAGEMENT_AFTER = "management_after"
    TREATMENT_FOR = "treatment_for"
    RESPONSE_AFTER = "response_after"
    RESULT_OF = "result_of"
    PARALLEL_TO = "parallel_to"
    OTHER_RELATION = "other_relation"


class ContextRole(StrEnum):
    INHERITED_CONTEXT = "inherited_context"
    LOCAL_CONTENT = "local_content"
    MODIFIER_CONTEXT = "modifier_context"
    NON_INHERITED_NOTE = "non_inherited_note"
    UNCERTAIN = "uncertain"


class AtomizationPolicy(StrEnum):
    GENERATE_ATOM = "generate_atom"
    GENERATE_ATOM_WITH_INHERITED_CONTEXT = (
        "generate_atom_with_inherited_context"
    )
    DO_NOT_GENERATE_CONTEXT_ONLY = "do_not_generate_context_only"
    GENERATE_GROUP_MODIFIER_ATOM = "generate_group_modifier_atom"
    DEFER = "defer"


class EvidenceFrameNode(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    frame_node_id: str = Field(default_factory=generate_evidence_frame_node_id)
    source_item_id: ItemID

    node_type: FrameNodeType
    node_text: str

    assertion_status: NegationStatus
    certainty: CertaintyLevel
    temporality: TemporalRelation

    parent_node_id: str | None = None
    relation_to_parent: FrameRelationType | None = None

    inherited_context_node_ids: list[str] = Field(default_factory=list)

    source_assertion_ids: list[str] = Field(
        default_factory=list,
        description=(
            "ClinicalObjectAssertion ids that this frame node represents or is grounded in. "
            "Every ClinicalObjectAssertion for the candidate must be mapped to at least one "
            "EvidenceFrameNode.source_assertion_ids unless explicitly deferred by the frame."
        ),
    )
    source_attribute_ids: list[str] = Field(default_factory=list)
    source_span_ids: list[SpanID] = Field(default_factory=list)

    context_role: ContextRole
    atomizable: bool
    atomization_policy: AtomizationPolicy

    confidence: ConfidenceLevel
    notes: str | None = None

    @field_validator("frame_node_id", "source_item_id", "node_text", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "Required text fields")

    @field_validator("notes", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator("source_assertion_ids", mode="after")
    @classmethod
    def normalize_source_assertion_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for assertion_id in value:
            normalized = normalize_optional_text(assertion_id)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned

    @model_validator(mode="after")
    def validate_parent_relation_consistency(self) -> "EvidenceFrameNode":
        if self.parent_node_id is None:
            if self.relation_to_parent not in {None, FrameRelationType.ROOT_OF}:
                raise ValueError(
                    "Root frame nodes must not have a non-root relation_to_parent."
                )
        elif self.relation_to_parent is None:
            raise ValueError(
                "Non-root frame nodes must define relation_to_parent."
            )

        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self


class EvidenceEventFrame(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    frame_id: str = Field(default_factory=generate_evidence_frame_id)
    source_item_id: ItemID
    source_text: str

    frame_nodes: list[EvidenceFrameNode] = Field(default_factory=list)
    deferred_assertion_ids: list[str] = Field(
        default_factory=list,
        description=(
            "ClinicalObjectAssertion ids that were not converted into frame nodes. "
            "Each deferred assertion must have a corresponding frame warning explaining why."
        ),
    )
    frame_warnings: list[AtomizationWarning] = Field(default_factory=list)

    @field_validator("frame_id", "source_item_id", "source_text", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "Required text fields")

    @field_validator("deferred_assertion_ids", mode="after")
    @classmethod
    def normalize_deferred_assertion_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for assertion_id in value:
            normalized = normalize_optional_text(assertion_id)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned

    @model_validator(mode="after")
    def validate_frame_integrity(self) -> "EvidenceEventFrame":
        node_ids = [node.frame_node_id for node in self.frame_nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("EvidenceEventFrame.frame_node_id values must be unique.")

        node_id_set = set(node_ids)
        for node in self.frame_nodes:
            if node.source_item_id != self.source_item_id:
                raise ValueError(
                    "Every frame node source_item_id must match frame.source_item_id."
                )
            if node.parent_node_id is not None and node.parent_node_id not in node_id_set:
                raise ValueError("parent_node_id must reference an existing node.")
            missing_context_ids = [
                context_id
                for context_id in node.inherited_context_node_ids
                if context_id not in node_id_set
            ]
            if missing_context_ids:
                raise ValueError(
                    "inherited_context_node_ids must reference existing nodes."
                )

        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self


class EvidenceEventFrameBuildResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    frames: list[EvidenceEventFrame] = Field(default_factory=list)
    warnings: list[AtomizationWarning] = Field(default_factory=list)
