"""JSON output skeletons for evidence_graph_structurer LLM calls."""

from __future__ import annotations

import json

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
            ],
            "assertion_issues": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "assertion_needs_review",
                    "message": "...",
                    "related_item_id": "item_001",
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def evidence_frame_output_skeleton() -> str:
    return json.dumps(
        {
            "evidence_frames": [
                {
                    "source_item_id": "item_001",
                    "frame_type": EvidenceFrameType.SYMPTOM_COURSE.value,
                    "frame_label": "10天前出现咳嗽、咳痰、痰中带血",
                    "member_assertion_ids": [
                        "clinical_object_assertion_xxx",
                        "clinical_object_assertion_yyy",
                    ],
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
            "frame_issues": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "frame_needs_review",
                    "message": "...",
                    "related_item_id": "item_001",
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def evidence_relation_output_skeleton() -> str:
    return json.dumps(
        {
            "evidence_relations": [
                {
                    "source_ref": "clinical_object_assertion_xxx",
                    "source_ref_type": EvidenceRefType.NODE.value,
                    "relation_type": EvidenceRelationType.HAS_TEMPORAL_CONTEXT.value,
                    "target_ref": "clinical_object_assertion_zzz",
                    "target_ref_type": EvidenceRefType.NODE.value,
                    "evidence_basis": EvidenceBasis.SOURCE_TEXT.value,
                    "confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
            "relation_issues": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "relation_needs_review",
                    "message": "...",
                    "related_item_id": "item_001",
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
