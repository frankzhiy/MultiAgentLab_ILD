"""Schema-contract snippets injected into Evidence Graph Structurer prompts."""

from __future__ import annotations

from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_graph_structurer.common import (
    ConfidenceLevel,
    ValidationSeverity,
)
from src.schemas.evidence_graph_structurer.evidence_frame import EvidenceFrameType
from src.schemas.evidence_graph_structurer.evidence_relation import (
    EvidenceBasis,
    EvidenceRefType,
    EvidenceRelationType,
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
        ("assertion_cue_text", "str|null", "Source-copied cue word."),
        ("assertion_scope_text", "str|null", "Source-copied scope phrase covering the object."),
        ("temporal_anchor_text", "str|null", "Source-copied time anchor scoping this assertion."),
        ("trigger_text", "str|null", "Source-copied trigger/cause phrase."),
        ("modifier_texts", "list[str]", "Source-copied modifier phrases attached to this assertion."),
        ("confidence", "enum", ", ".join(value.value for value in ConfidenceLevel)),
        ("notes", "str|null", "Optional short note; no inferred clinical reasoning."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def assertion_issue_fields() -> str:
    rows = [
        ("severity", "enum", ", ".join(value.value for value in ValidationSeverity)),
        ("code", "str", "Short snake_case code, e.g. assertion_needs_review."),
        ("message", "str", "Human-readable explanation."),
        ("related_item_id", "str|null", "Source item id this issue is about."),
        ("related_assertion_id", "str|null", "Related ClinicalObjectAssertion id."),
        ("related_frame_id", "str|null", "Related EvidenceFrame id."),
        ("related_node_id", "str|null", "Related EvidenceNode id."),
        ("related_relation_id", "str|null", "Related EvidenceRelation id."),
        ("related_span_id", "str|null", "Source span id this issue is about."),
        ("details", "str|null", "Optional detail."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def evidence_frame_fields() -> str:
    rows = [
        ("source_item_id", "str", "Must equal the item_id of the input item."),
        (
            "frame_type",
            "enum",
            ", ".join(value.value for value in EvidenceFrameType),
        ),
        ("frame_label", "str", "Human-readable label for this frame."),
        (
            "member_assertion_ids",
            "list[str]",
            "Object_ids of ClinicalObjectAssertions that belong to this frame.",
        ),
        ("confidence", "enum", ", ".join(value.value for value in ConfidenceLevel)),
        ("notes", "str|null", "Optional short note."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def evidence_relation_fields() -> str:
    rows = [
        (
            "source_ref",
            "str",
            "Endpoint id: a ClinicalObjectAssertion id (node) or EvidenceFrame id (frame).",
        ),
        ("source_ref_type", "enum", ", ".join(v.value for v in EvidenceRefType)),
        (
            "relation_type",
            "enum",
            ", ".join(v.value for v in EvidenceRelationType),
        ),
        (
            "target_ref",
            "str",
            "Endpoint id: a ClinicalObjectAssertion id (node) or EvidenceFrame id (frame).",
        ),
        ("target_ref_type", "enum", ", ".join(v.value for v in EvidenceRefType)),
        ("evidence_basis", "enum", ", ".join(v.value for v in EvidenceBasis)),
        ("confidence", "enum", ", ".join(v.value for v in ConfidenceLevel)),
        ("notes", "str|null", "Optional short note."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)
