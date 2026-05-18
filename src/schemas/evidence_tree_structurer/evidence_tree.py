"""EvidenceTree schema for hierarchical structured evidence."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.utils.id_generator import (
    generate_evidence_tree_id,
    generate_evidence_tree_node_id,
)

from .tree_structuring_warning import TreeStructuringWarning
from .common import (
    CertaintyLevel,
    ConfidenceLevel,
    EvidenceTreeID,
    EvidenceTreeNodeID,
    ItemID,
    NegationStatus,
    SpanID,
    TemporalRelation,
    normalize_optional_text,
    require_non_empty_text,
    validate_no_forbidden_schema_fields,
)


class EvidenceTreeNodeType(StrEnum):
    """Closed vocabulary of EvidenceTree node types.

    The instance-level tree shape (depth, branching, root count) is
    unconstrained; only the type vocabulary and parent-child grammar
    (see ``ALLOWED_PARENT_TYPES`` below) are closed.
    """

    # --- Context layer -------------------------------------------------
    TEMPORAL_CONTEXT = "temporal_context"
    TRIGGER = "trigger"
    BACKGROUND_STATE = "background_state"
    EXPOSURE_OR_RISK_FACTOR = "exposure_or_risk_factor"

    # --- Event layer ---------------------------------------------------
    MAIN_EVENT = "main_event"
    MANAGEMENT_EVENT = "management_event"
    TREATMENT_EVENT = "treatment_event"
    TEST_EVENT = "test_event"
    TREATMENT_RESPONSE = "treatment_response"

    # --- Content layer -------------------------------------------------
    CLINICAL_OBJECT = "clinical_object"
    OBJECT_PROPERTY = "object_property"
    EVENT_MODIFIER = "event_modifier"
    TEST_FINDING = "test_finding"
    DIAGNOSTIC_IMPRESSION = "diagnostic_impression"
    NEGATIVE_FINDING = "negative_finding"

    # --- Fallback ------------------------------------------------------
    UNCERTAIN_OR_OTHER = "uncertain_or_other"


class EvidenceTreeRelationType(StrEnum):
    ROOT_OF = "root_of"
    TEMPORAL_CONTEXT_OF = "temporal_context_of"
    BACKGROUND_CONTEXT_OF = "background_context_of"
    TRIGGER_CONTEXT_OF = "trigger_context_of"
    OCCURRENCE_OF = "occurrence_of"
    ASSOCIATED_WITH = "associated_with"
    PROPERTY_OF = "property_of"
    MODIFIER_OF = "modifier_of"
    NEGATIVE_CONTRAST_OF = "negative_contrast_of"
    REASON_FOR_MANAGEMENT = "reason_for_management"
    MANAGEMENT_AFTER = "management_after"
    TREATMENT_FOR = "treatment_for"
    RESPONSE_AFTER = "response_after"
    RESULT_OF = "result_of"
    FINDING_OF = "finding_of"
    IMPRESSION_OF = "impression_of"
    PARALLEL_TO = "parallel_to"
    OTHER_RELATION = "other_relation"


# ---------------------------------------------------------------------
# Parent-child grammar table (closed type-level rules, open tree shape)
# ---------------------------------------------------------------------

#: Node types that may appear as a tree root (parent_node_id is None).
ROOT_ALLOWED_NODE_TYPES: frozenset[EvidenceTreeNodeType] = frozenset(
    {
        EvidenceTreeNodeType.TEMPORAL_CONTEXT,
        EvidenceTreeNodeType.BACKGROUND_STATE,
        EvidenceTreeNodeType.EXPOSURE_OR_RISK_FACTOR,
        EvidenceTreeNodeType.MAIN_EVENT,
        EvidenceTreeNodeType.MANAGEMENT_EVENT,
        EvidenceTreeNodeType.TREATMENT_EVENT,
        EvidenceTreeNodeType.TEST_EVENT,
        EvidenceTreeNodeType.UNCERTAIN_OR_OTHER,
    }
)

#: Node types that must be leaves (no children allowed).
LEAF_NODE_TYPES: frozenset[EvidenceTreeNodeType] = frozenset(
    {
        EvidenceTreeNodeType.OBJECT_PROPERTY,
        EvidenceTreeNodeType.EVENT_MODIFIER,
        EvidenceTreeNodeType.NEGATIVE_FINDING,
    }
)

#: Pure-context node types that only scope descendant evidence nodes.
CONTEXT_ONLY_NODE_TYPES: frozenset[EvidenceTreeNodeType] = frozenset(
    {
        EvidenceTreeNodeType.TEMPORAL_CONTEXT,
        EvidenceTreeNodeType.TRIGGER,
    }
)

#: Allowed parent node types for each child node type.
#:
#: A value of ``None`` means any parent type is acceptable (used by the
#: fallback ``UNCERTAIN_OR_OTHER`` to keep the graph repairable).
#: An empty frozenset means the type may only appear as a root.
ALLOWED_PARENT_TYPES: dict[
    EvidenceTreeNodeType,
    frozenset[EvidenceTreeNodeType] | None,
] = {
    EvidenceTreeNodeType.TEMPORAL_CONTEXT: frozenset(),
    EvidenceTreeNodeType.BACKGROUND_STATE: frozenset(
        {EvidenceTreeNodeType.TEMPORAL_CONTEXT}
    ),
    EvidenceTreeNodeType.EXPOSURE_OR_RISK_FACTOR: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.BACKGROUND_STATE,
        }
    ),
    EvidenceTreeNodeType.TRIGGER: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.MAIN_EVENT,
        }
    ),
    EvidenceTreeNodeType.MAIN_EVENT: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.TRIGGER,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
        }
    ),
    EvidenceTreeNodeType.MANAGEMENT_EVENT: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.MAIN_EVENT,
            EvidenceTreeNodeType.TREATMENT_RESPONSE,
            EvidenceTreeNodeType.TEST_EVENT,
        }
    ),
    EvidenceTreeNodeType.TREATMENT_EVENT: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
            EvidenceTreeNodeType.TREATMENT_RESPONSE,
        }
    ),
    EvidenceTreeNodeType.TEST_EVENT: frozenset(
        {
            EvidenceTreeNodeType.TEMPORAL_CONTEXT,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
        }
    ),
    EvidenceTreeNodeType.TREATMENT_RESPONSE: frozenset(
        {EvidenceTreeNodeType.TREATMENT_EVENT}
    ),
    EvidenceTreeNodeType.CLINICAL_OBJECT: frozenset(
        {
            EvidenceTreeNodeType.MAIN_EVENT,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
            EvidenceTreeNodeType.CLINICAL_OBJECT,
        }
    ),
    EvidenceTreeNodeType.TEST_FINDING: frozenset({EvidenceTreeNodeType.TEST_EVENT}),
    EvidenceTreeNodeType.DIAGNOSTIC_IMPRESSION: frozenset(
        {
            EvidenceTreeNodeType.TEST_EVENT,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
            EvidenceTreeNodeType.MAIN_EVENT,
        }
    ),
    EvidenceTreeNodeType.OBJECT_PROPERTY: frozenset(
        {
            EvidenceTreeNodeType.CLINICAL_OBJECT,
            EvidenceTreeNodeType.TEST_FINDING,
            EvidenceTreeNodeType.EXPOSURE_OR_RISK_FACTOR,
            EvidenceTreeNodeType.DIAGNOSTIC_IMPRESSION,
        }
    ),
    EvidenceTreeNodeType.EVENT_MODIFIER: frozenset(
        {
            EvidenceTreeNodeType.MAIN_EVENT,
            EvidenceTreeNodeType.TREATMENT_EVENT,
            EvidenceTreeNodeType.TEST_EVENT,
            EvidenceTreeNodeType.CLINICAL_OBJECT,
        }
    ),
    EvidenceTreeNodeType.NEGATIVE_FINDING: frozenset(
        {
            EvidenceTreeNodeType.MAIN_EVENT,
            EvidenceTreeNodeType.MANAGEMENT_EVENT,
            EvidenceTreeNodeType.BACKGROUND_STATE,
            EvidenceTreeNodeType.TEST_EVENT,
            EvidenceTreeNodeType.TEST_FINDING,
        }
    ),
    EvidenceTreeNodeType.UNCERTAIN_OR_OTHER: None,
}


class ContextRole(StrEnum):
    INHERITED_CONTEXT = "inherited_context"
    LOCAL_CONTENT = "local_content"
    MODIFIER_CONTEXT = "modifier_context"
    NON_INHERITED_NOTE = "non_inherited_note"
    UNCERTAIN = "uncertain"


class EvidenceTreeNodeOrigin(StrEnum):
    """How an EvidenceTreeNode is grounded.

    ``ClinicalObjectAssertion`` is an important source, but tree nodes may
    also be created from local context/modifier/property text or introduced as
    structural grouping nodes that organize source-grounded descendants.
    """

    ASSERTION_BACKED = "assertion_backed"
    CONTEXT_BACKED = "context_backed"
    STRUCTURAL_GROUP = "structural_group"


class EvidenceTreeNode(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    tree_node_id: EvidenceTreeNodeID = Field(
        default_factory=generate_evidence_tree_node_id,
    )
    source_item_id: ItemID

    node_type: EvidenceTreeNodeType
    node_text: str

    assertion_status: NegationStatus
    certainty: CertaintyLevel
    temporality: TemporalRelation

    parent_node_id: str | None = None
    relation_to_parent: EvidenceTreeRelationType | None = None

    inherited_context_node_ids: list[str] = Field(default_factory=list)

    source_assertion_ids: list[str] = Field(
        default_factory=list,
        description=(
            "ClinicalObjectAssertion ids that this tree node represents or is grounded in. "
            "Every ClinicalObjectAssertion for the candidate must be mapped to at least one "
            "EvidenceTreeNode.source_assertion_ids unless explicitly deferred by the tree."
        ),
    )
    source_attribute_ids: list[str] = Field(
        default_factory=list,
        description="ClinicalAttribute ids that grounded this context/property/modifier node.",
    )
    source_span_ids: list[SpanID] = Field(default_factory=list)

    node_origin: EvidenceTreeNodeOrigin = Field(
        ...,
        description=(
            "Whether this node is grounded by ClinicalObjectAssertion ids, "
            "local context/property/modifier text, or structural grouping."
        ),
    )
    context_role: ContextRole

    confidence: ConfidenceLevel
    notes: str | None = None

    @field_validator("tree_node_id", "source_item_id", "node_text", mode="after")
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

    @field_validator(
        "source_attribute_ids",
        "source_span_ids",
        "inherited_context_node_ids",
        mode="after",
    )
    @classmethod
    def normalize_id_lists(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw_id in value:
            normalized = normalize_optional_text(raw_id)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned

    @model_validator(mode="after")
    def validate_origin_consistency(self) -> "EvidenceTreeNode":
        if (
            self.node_origin == EvidenceTreeNodeOrigin.ASSERTION_BACKED
            and not self.source_assertion_ids
        ):
            raise ValueError(
                "assertion_backed tree nodes must contain source_assertion_ids."
            )
        if (
            self.node_origin != EvidenceTreeNodeOrigin.ASSERTION_BACKED
            and self.source_assertion_ids
        ):
            raise ValueError(
                "Only assertion_backed tree nodes may contain source_assertion_ids."
            )
        if (
            self.node_origin == EvidenceTreeNodeOrigin.CONTEXT_BACKED
            and not self.source_span_ids
            and not self.source_attribute_ids
        ):
            raise ValueError(
                "context_backed tree nodes must contain source_span_ids or source_attribute_ids."
            )
        return self

    @model_validator(mode="after")
    def validate_parent_relation_consistency(self) -> "EvidenceTreeNode":
        if self.parent_node_id is None:
            if self.relation_to_parent not in {
                None,
                EvidenceTreeRelationType.ROOT_OF,
            }:
                raise ValueError(
                    "Root tree nodes must not have a non-root relation_to_parent."
                )
        elif self.relation_to_parent is None:
            raise ValueError(
                "Non-root tree nodes must define relation_to_parent."
            )

        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self


class EvidenceTree(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    tree_id: EvidenceTreeID = Field(
        default_factory=generate_evidence_tree_id,
    )
    source_item_id: ItemID
    source_text: str

    tree_nodes: list[EvidenceTreeNode] = Field(
        default_factory=list,
    )
    deferred_assertion_ids: list[str] = Field(
        default_factory=list,
        description=(
            "ClinicalObjectAssertion ids that were not converted into tree nodes. "
            "Each deferred assertion must have a corresponding tree warning explaining why."
        ),
    )
    tree_warnings: list[TreeStructuringWarning] = Field(
        default_factory=list,
    )

    @field_validator("tree_id", "source_item_id", "source_text", mode="after")
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
    def validate_tree_integrity(self) -> "EvidenceTree":
        node_ids = [node.tree_node_id for node in self.tree_nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("EvidenceTree.tree_node_id values must be unique.")

        node_id_set = set(node_ids)
        for node in self.tree_nodes:
            if node.source_item_id != self.source_item_id:
                raise ValueError(
                    "Every tree node source_item_id must match tree.source_item_id."
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


class EvidenceTreeBuildResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    evidence_trees: list[EvidenceTree] = Field(
        default_factory=list,
    )
    warnings: list[TreeStructuringWarning] = Field(default_factory=list)
