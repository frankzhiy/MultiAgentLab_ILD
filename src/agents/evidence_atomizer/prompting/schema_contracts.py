from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Any

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
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)


def evidence_atomization_contract() -> dict[str, Any]:
    return {
        "evidence_atom_draft_fields": _lines(
            [
                "draft_id: temporary id for this response only",
                "coverage_unit_ids: required coverage unit ids covered by this draft",
                "evidence_type: source-level evidence category",
                "clinical_domain: routing domain, not diagnosis",
                "granularity: atom boundary quality",
                "statement: minimal source-grounded evidence statement",
                "normalized_label",
                "assertion_status, certainty, temporality",
                "source_item_ids, source_attribute_ids, source_span_ids",
                "source_frame_node_ids, context_frame_node_ids, parent_frame_node_ids",
                "atom_context_text, local_content_text",
                "atomization_confidence, notes",
            ]
        ),
        "item_evidence_link_draft_fields": _lines(
            [
                "item_id",
                "evidence_atom_draft_ids or draft_ids",
                "transformation_type",
                "explanation",
            ]
        ),
        "deferred_item_draft_fields": _lines(
            [
                "item_id",
                "reason",
                "explanation",
                "related_span_ids",
            ]
        ),
        "atomization_warning_draft_fields": _lines(
            [
                "severity",
                "code",
                "message",
                "related_item_id",
                "related_evidence_id only if referring to a temporary draft id",
                "related_span_id",
            ]
        ),
        "allowed_evidence_type_values": _format_enum_values(EvidenceType),
        "allowed_clinical_domain_values": _format_enum_values(ClinicalDomain),
        "allowed_granularity_values": _format_enum_values(EvidenceGranularity),
        "allowed_negation_values": _format_enum_values(NegationStatus),
        "allowed_certainty_values": _format_enum_values(CertaintyLevel),
        "allowed_temporality_values": _format_enum_values(TemporalRelation),
        "allowed_confidence_values": _format_enum_values(ConfidenceLevel),
        "allowed_transformation_values": _format_enum_values(
            AtomizationTransformationType
        ),
        "allowed_deferred_reason_values": _format_enum_values(DeferredReason),
        "allowed_warning_severity_values": _format_enum_values(ValidationSeverity),
        "persistent_id_policy": _lines(
            [
                "Do not generate persistent evidence_id values.",
                "Do not generate atomization_result_id values.",
                "Temporary draft ids are allowed only for links inside this response.",
                "Code will replace temporary draft ids with persistent ids.",
            ]
        ),
        "code_filled_provenance_policy": _lines(
            [
                "Do not output source_contexts.",
                "ClinicalSection provenance will be filled by code from source_item_ids.",
                "Do not guess section_type or section_title.",
                "Do not output source_text.",
                "EvidenceAtom.source_text will be filled by code from source_span_ids.",
            ]
        ),
        "forbidden_reasoning_policy": _lines(
            [
                "Do not include support or refute relationships.",
                "Do not infer IPF, CTD-ILD, HP, infection, AE, or any diagnosis.",
                "Do not recommend treatment or action.",
                "Do not create conflict, update, safety gate, or arbitration fields.",
            ]
        ),
    }


def clinical_assertion_labeling_contract() -> dict[str, Any]:
    return {
        "clinical_object_assertion_fields": _lines(
            [
                "source_item_id: must match the input candidate item_id",
                "object_text: exact contiguous text copied from source_text",
                "object_type",
                "assertion_status",
                "assertion_cue_text: exact cue text copied from source_text or null",
                "assertion_scope_text: exact scope text copied from source_text or null",
                "confidence",
                "notes",
            ]
        ),
        "assertion_warning_fields": _lines(
            [
                "severity",
                "code",
                "message",
                "related_item_id",
                "related_span_id",
            ]
        ),
        "allowed_object_type_values": _format_enum_values(ClinicalObjectType),
        "allowed_assertion_status_values": _format_enum_values(
            ClinicalObjectAssertionStatus
        ),
        "allowed_confidence_values": _format_enum_values(ConfidenceLevel),
        "allowed_warning_severity_values": _format_enum_values(ValidationSeverity),
    }


def _format_enum_values(enum_cls: type[StrEnum]) -> str:
    return _lines(item.value for item in enum_cls)


def _lines(values: Iterable[str]) -> str:
    return "\n".join(f"- {value}" for value in values)
