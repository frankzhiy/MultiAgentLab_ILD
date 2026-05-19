"""Evidence Graph Structurer schemas package."""

from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "CaseID",
    "CertaintyLevel",
    "ClinicalAssertionResolutionResult",
    "ClinicalObjectAssertion",
    "ClinicalObjectAssertionStatus",
    "ClinicalObjectType",
    "ConfidenceLevel",
    "EvidenceBasis",
    "EvidenceFrame",
    "EvidenceFrameType",
    "EvidenceGraphValidationReport",
    "EvidenceGraphValidationStatus",
    "EvidenceGraphlet",
    "EvidenceGraphletStatus",
    "EvidenceNode",
    "EvidenceNodeType",
    "EvidenceRefType",
    "EvidenceRelation",
    "EvidenceRelationType",
    "EvidenceStructuringIssue",
    "EvidenceStructuringResult",
    "InputID",
    "ItemID",
    "NegationStatus",
    "RELATION_COMPATIBILITY",
    "SpanID",
    "StageID",
    "TemporalRelation",
    "ValidationSeverity",
    "endpoint_kind",
    "is_endpoint_allowed",
]

if TYPE_CHECKING:
    from .clinical_object_assertion import (
        ClinicalAssertionResolutionResult,
        ClinicalObjectAssertion,
        ClinicalObjectAssertionStatus,
        ClinicalObjectType,
    )
    from .common import (
        CaseID,
        CertaintyLevel,
        ConfidenceLevel,
        InputID,
        ItemID,
        NegationStatus,
        SpanID,
        StageID,
        TemporalRelation,
        ValidationSeverity,
    )
    from .evidence_frame import EvidenceFrame, EvidenceFrameType
    from .evidence_graph_validation import (
        EvidenceGraphValidationReport,
        EvidenceGraphValidationStatus,
    )
    from .evidence_graphlet import EvidenceGraphlet, EvidenceGraphletStatus
    from .evidence_issue import EvidenceStructuringIssue
    from .evidence_node import EvidenceNode, EvidenceNodeType
    from .evidence_relation import (
        RELATION_COMPATIBILITY,
        EvidenceBasis,
        EvidenceRefType,
        EvidenceRelation,
        EvidenceRelationType,
        endpoint_kind,
        is_endpoint_allowed,
    )
    from .evidence_structuring_result import EvidenceStructuringResult


_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "ClinicalAssertionResolutionResult": (
        ".clinical_object_assertion",
        "ClinicalAssertionResolutionResult",
    ),
    "ClinicalObjectAssertion": (".clinical_object_assertion", "ClinicalObjectAssertion"),
    "ClinicalObjectAssertionStatus": (
        ".clinical_object_assertion",
        "ClinicalObjectAssertionStatus",
    ),
    "ClinicalObjectType": (".clinical_object_assertion", "ClinicalObjectType"),
    "CaseID": (".common", "CaseID"),
    "CertaintyLevel": (".common", "CertaintyLevel"),
    "ConfidenceLevel": (".common", "ConfidenceLevel"),
    "InputID": (".common", "InputID"),
    "ItemID": (".common", "ItemID"),
    "NegationStatus": (".common", "NegationStatus"),
    "SpanID": (".common", "SpanID"),
    "StageID": (".common", "StageID"),
    "TemporalRelation": (".common", "TemporalRelation"),
    "ValidationSeverity": (".common", "ValidationSeverity"),
    "EvidenceFrame": (".evidence_frame", "EvidenceFrame"),
    "EvidenceFrameType": (".evidence_frame", "EvidenceFrameType"),
    "EvidenceGraphValidationReport": (
        ".evidence_graph_validation",
        "EvidenceGraphValidationReport",
    ),
    "EvidenceGraphValidationStatus": (
        ".evidence_graph_validation",
        "EvidenceGraphValidationStatus",
    ),
    "EvidenceGraphlet": (".evidence_graphlet", "EvidenceGraphlet"),
    "EvidenceGraphletStatus": (".evidence_graphlet", "EvidenceGraphletStatus"),
    "EvidenceStructuringIssue": (".evidence_issue", "EvidenceStructuringIssue"),
    "EvidenceNode": (".evidence_node", "EvidenceNode"),
    "EvidenceNodeType": (".evidence_node", "EvidenceNodeType"),
    "EvidenceBasis": (".evidence_relation", "EvidenceBasis"),
    "EvidenceRefType": (".evidence_relation", "EvidenceRefType"),
    "EvidenceRelation": (".evidence_relation", "EvidenceRelation"),
    "EvidenceRelationType": (".evidence_relation", "EvidenceRelationType"),
    "RELATION_COMPATIBILITY": (".evidence_relation", "RELATION_COMPATIBILITY"),
    "endpoint_kind": (".evidence_relation", "endpoint_kind"),
    "is_endpoint_allowed": (".evidence_relation", "is_endpoint_allowed"),
    "EvidenceStructuringResult": (
        ".evidence_structuring_result",
        "EvidenceStructuringResult",
    ),
}


def __getattr__(name: str):  # pragma: no cover - thin lazy loader
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module {__name__} has no attribute {name!r}")
    import importlib

    module_name, attr_name = _LAZY_IMPORTS[name]
    module = importlib.import_module(module_name, package=__name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(__all__) | set(globals()))
