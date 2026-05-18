"""JSON output skeletons for evidence_tree_structurer LLM calls."""

from __future__ import annotations

import json

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
)


def clinical_assertion_output_skeleton() -> str:
    return json.dumps(
        {
            "clinical_object_assertions": [
                {
                    "source_item_id": "item_001",
                    "object_text": "咳嗽",
                    "object_type": ClinicalObjectType.SYMPTOM.value,
                    "assertion_status": ClinicalObjectAssertionStatus.PRESENT.value,
                    "assertion_cue_text": "出现",
                    "assertion_scope_text": "出现咳嗽",
                    "temporal_anchor_text": "10天前",
                    "trigger_text": "无明显诱因",
                    "modifier_texts": ["晨起"],
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                },
                {
                    "source_item_id": "item_001",
                    "object_text": "痰中带血",
                    "object_type": ClinicalObjectType.SYMPTOM.value,
                    "assertion_status": ClinicalObjectAssertionStatus.PRESENT.value,
                    "assertion_cue_text": "伴",
                    "assertion_scope_text": "伴痰中带血",
                    "temporal_anchor_text": "10天前",
                    "trigger_text": None,
                    "modifier_texts": [],
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                },
            ],
            "assertion_warnings": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "assertion_needs_review",
                    "message": "...",
                    "related_item_id": "item_001",
                    "related_span_id": None,
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def evidence_tree_output_skeleton(item_id: str) -> str:
    return json.dumps(
        {
            "tree_nodes": [
                {
                    "raw_id": "n1",
                    "source_item_id": item_id,
                    "node_type": EvidenceTreeNodeType.TEMPORAL_CONTEXT.value,
                    "node_text": "10天前",
                    "assertion_status": "present",
                    "certainty": "definite",
                    "temporality": "past",
                    "parent_raw_id": None,
                    "relation_to_parent": EvidenceTreeRelationType.ROOT_OF.value,
                    "inherited_context_raw_ids": [],
                    "source_assertion_ids": [],
                    "source_span_ids": ["span_001"],
                    "node_origin": EvidenceTreeNodeOrigin.CONTEXT_BACKED.value,
                    "context_role": ContextRole.INHERITED_CONTEXT.value,
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                },
                {
                    "raw_id": "n2",
                    "source_item_id": item_id,
                    "node_type": EvidenceTreeNodeType.MAIN_EVENT.value,
                    "node_text": "出现咳嗽",
                    "assertion_status": "present",
                    "certainty": "definite",
                    "temporality": "past",
                    "parent_raw_id": "n1",
                    "relation_to_parent": EvidenceTreeRelationType.TEMPORAL_CONTEXT_OF.value,
                    "inherited_context_raw_ids": [],
                    "source_assertion_ids": [],
                    "source_span_ids": ["span_001"],
                    "node_origin": EvidenceTreeNodeOrigin.STRUCTURAL_GROUP.value,
                    "context_role": ContextRole.LOCAL_CONTENT.value,
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                },
                {
                    "raw_id": "n3",
                    "source_item_id": item_id,
                    "node_type": EvidenceTreeNodeType.CLINICAL_OBJECT.value,
                    "node_text": "咳嗽",
                    "assertion_status": "present",
                    "certainty": "definite",
                    "temporality": "past",
                    "parent_raw_id": "n2",
                    "relation_to_parent": EvidenceTreeRelationType.ASSOCIATED_WITH.value,
                    "inherited_context_raw_ids": ["n1"],
                    "source_assertion_ids": ["clinical_object_assertion_..."],
                    "source_span_ids": ["span_001"],
                    "node_origin": EvidenceTreeNodeOrigin.ASSERTION_BACKED.value,
                    "context_role": ContextRole.LOCAL_CONTENT.value,
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                },
            ],
            "deferred_assertion_ids": [],
            "tree_warnings": [],
        },
        ensure_ascii=False,
        indent=2,
    )
