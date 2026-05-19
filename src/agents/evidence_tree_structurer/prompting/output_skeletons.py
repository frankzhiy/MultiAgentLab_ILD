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
