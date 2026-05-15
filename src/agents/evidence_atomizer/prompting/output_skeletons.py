from __future__ import annotations

import json

from src.schemas.evidence_atomizer.common import (
    AtomizationTransformationType,
    CertaintyLevel,
    ClinicalDomain,
    ConfidenceLevel,
    DeferredReason,
    EvidenceGranularity,
    EvidenceType,
    NegationStatus,
    TemporalRelation,
    ValidationSeverity,
)


def evidence_atomization_skeleton() -> str:
    return json.dumps(
        {
            "evidence_atom_drafts": [
                {
                    "draft_id": "draft_001",
                    "coverage_unit_ids": ["item_001__unit_001"],
                    "evidence_type": EvidenceType.SYMPTOM.value,
                    "clinical_domain": ClinicalDomain.RESPIRATORY.value,
                    "granularity": EvidenceGranularity.ATOMIC.value,
                    "statement": "...",
                    "normalized_label": "...",
                    "value": None,
                    "unit": None,
                    "body_site": None,
                    "assertion_status": NegationStatus.PRESENT.value,
                    "certainty": CertaintyLevel.DEFINITE.value,
                    "temporality": TemporalRelation.UNKNOWN.value,
                    "time_text": None,
                    "source_item_ids": ["item_001"],
                    "source_span_ids": ["span_item_001"],
                    "source_text": "...",
                    "atomization_confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
            "item_to_evidence_links": [
                {
                    "item_id": "item_001",
                    "evidence_atom_draft_ids": ["draft_001"],
                    "transformation_type": AtomizationTransformationType.COPIED.value,
                    "explanation": None,
                }
            ],
            "deferred_items": [
                {
                    "item_id": "item_002",
                    "reason": DeferredReason.TOO_AMBIGUOUS.value,
                    "explanation": "...",
                    "related_span_ids": ["span_item_002"],
                }
            ],
            "atomization_warnings": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "atomization_uncertain",
                    "message": "...",
                    "related_item_id": "item_001",
                    "related_evidence_id": None,
                    "related_span_id": None,
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
