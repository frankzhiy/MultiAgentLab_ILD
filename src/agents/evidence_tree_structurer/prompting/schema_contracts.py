"""Schema-contract snippets injected into LLM prompts."""

from __future__ import annotations

from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_tree_structurer.common import (
    ConfidenceLevel,
    ValidationSeverity,
)
from src.schemas.evidence_tree_structurer.evidence_tree import (
    ContextRole,
    EvidenceTreeNodeOrigin,
    EvidenceTreeNodeType,
    EvidenceTreeRelationType,
    LEAF_NODE_TYPES,
    ROOT_ALLOWED_NODE_TYPES,
    CONTEXT_ONLY_NODE_TYPES,
)


def clinical_object_assertion_fields() -> str:
    rows = [
        ("source_item_id", "str", "Must equal the item_id of the input item."),
        ("object_text", "str", "Exact substring of source_text."),
        (
            "object_type",
            "enum",
            ", ".join(
                value.value
                for value in ClinicalObjectType
                if value is not ClinicalObjectType.UNCERTAIN
            ),
        ),
        (
            "assertion_status",
            "enum",
            ", ".join(value.value for value in ClinicalObjectAssertionStatus),
        ),
        ("assertion_cue_text", "str|null", "Source-copied cue word (e.g. 出现, 否认, 无)."),
        ("assertion_scope_text", "str|null", "Source-copied scope phrase covering the object."),
        (
            "temporal_anchor_text",
            "str|null",
            "Source-copied time anchor scoping this assertion (e.g. 10天前, 入院当日).",
        ),
        (
            "trigger_text",
            "str|null",
            "Source-copied trigger/cause phrase (e.g. 受凉后, 无明显诱因).",
        ),
        (
            "modifier_texts",
            "list[str]",
            "Source-copied modifier phrases attached to this assertion.",
        ),
        (
            "confidence",
            "enum",
            ", ".join(value.value for value in ConfidenceLevel),
        ),
        ("notes", "str|null", "Optional short note; no inferred clinical reasoning."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def assertion_warning_fields() -> str:
    rows = [
        ("severity", "enum", ", ".join(value.value for value in ValidationSeverity)),
        ("code", "str", "Short snake_case code, e.g. assertion_needs_review."),
        ("message", "str", "Human-readable explanation."),
        ("related_item_id", "str|null", "Source item id this warning is about."),
        ("related_span_id", "str|null", "Source span id this warning is about."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def evidence_tree_node_fields() -> str:
    rows = [
        ("raw_id", "str", "Unique within this tree response."),
        ("source_item_id", "str", "item_id of the item this tree is about."),
        (
            "node_type",
            "enum",
            ", ".join(value.value for value in EvidenceTreeNodeType),
        ),
        ("node_text", "str", "Exact substring of the item's source_text."),
        ("assertion_status", "str", "present | absent | possible | uncertain."),
        ("certainty", "str", "definite | probable | possible | uncertain."),
        (
            "temporality",
            "str",
            "Inherit from the StructuredClinicalItem temporality.",
        ),
        ("parent_raw_id", "str|null", "raw_id of parent node in this response. null only for the root."),
        (
            "relation_to_parent",
            "enum",
            ", ".join(value.value for value in EvidenceTreeRelationType),
        ),
        (
            "inherited_context_raw_ids",
            "list[str]",
            "raw_ids of context nodes (temporal_context / trigger) that scope this node.",
        ),
        (
            "source_assertion_ids",
            "list[str]",
            "object_id list of ClinicalObjectAssertion(s) this node represents (required for assertion-backed leaves).",
        ),
        (
            "source_span_ids",
            "list[str]",
            "span_id list this node ultimately traces back to.",
        ),
        (
            "node_origin",
            "enum",
            ", ".join(value.value for value in EvidenceTreeNodeOrigin),
        ),
        (
            "context_role",
            "enum",
            ", ".join(value.value for value in ContextRole),
        ),
        (
            "confidence",
            "enum",
            ", ".join(value.value for value in ConfidenceLevel),
        ),
        ("notes", "str|null", "Optional short note."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def evidence_tree_grammar_summary() -> str:
    return "\n".join(
        [
            "Allowed root node_types: "
            + ", ".join(t.value for t in ROOT_ALLOWED_NODE_TYPES),
            "Leaf node_types (must not have children): "
            + ", ".join(t.value for t in LEAF_NODE_TYPES),
            "Context-only node_types (temporal_context / trigger) scope the main_event subtree.",
            "Every assertion in the input must appear in exactly one assertion-backed node "
            "via source_assertion_ids, OR be listed in deferred_assertion_ids with a tree_warning.",
            "Guidance for choosing parent/child structure:",
            "  - Read source_text and assertion fields (object_text, object_type, assertion_status, "
            "temporal_anchor_text, trigger_text, modifier_texts) and decide which assertion is the "
            "main clinical event of this item; that becomes the main_event subtree.",
            "  - temporal_anchor_text values shared across assertions => one temporal_context node "
            "scoping the main_event.",
            "  - trigger_text values => trigger node under temporal_context or main_event.",
            "  - modifier_texts on an assertion => object_property leaves under that assertion's "
            "clinical_object node.",
            "  - Assertions that describe the same main_event (e.g. accompanying symptoms) become "
            "clinical_object siblings under main_event.",
            "  - Negated assertions (assertion_status=absent) stay attached to the most specific "
            "clinical_object they qualify, with the same source-grounded structure.",
            "  - When the source text does not justify a parent link, attach the node directly under "
            "main_event (or under the tree root if no main_event applies).",
        ]
    )
