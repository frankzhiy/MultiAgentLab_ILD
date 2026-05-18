"""Public exports for Evidence Tree Structurer schemas."""

from __future__ import annotations

from importlib import import_module

from .common import (
    TreeStructuringTransformationType,
    CaseID,
    CertaintyLevel,
    ConfidenceLevel,
    DeferredReason,
    EvidenceTreeStructuringResultID,
    EvidenceTreeID,
    EvidenceTreeNodeID,
    InputID,
    ItemID,
    NegationStatus,
    SpanID,
    StageID,
    TemporalRelation,
    ValidationSeverity,
)


_LAZY_EXPORTS = {
    "ClinicalAssertionResolutionResult": ".clinical_object_assertion",
    "ClinicalObjectAssertion": ".clinical_object_assertion",
    "ClinicalObjectAssertionStatus": ".clinical_object_assertion",
    "ClinicalObjectType": ".clinical_object_assertion",
    "EvidenceTree": ".evidence_tree",
    "EvidenceTreeBuildResult": ".evidence_tree",
    "EvidenceTreeNode": ".evidence_tree",
    "EvidenceTreeNodeOrigin": ".evidence_tree",
    "EvidenceTreeNodeType": ".evidence_tree",
    "EvidenceTreeRelationType": ".evidence_tree",
    "ContextRole": ".evidence_tree",
    "ItemEvidenceTreeLink": ".item_evidence_link",
    "DeferredStructuredItem": ".deferred_item",
    "TreeStructuringWarning": ".tree_structuring_warning",
    "EvidenceTreeStructuringResult": ".evidence_tree_structuring_result",
}

__all__ = [
    "TreeStructuringTransformationType",
    "TreeStructuringWarning",
    "CaseID",
    "CertaintyLevel",
    "ClinicalAssertionResolutionResult",
    "ClinicalObjectAssertion",
    "ClinicalObjectAssertionStatus",
    "ClinicalObjectType",
    "ConfidenceLevel",
    "ContextRole",
    "DeferredReason",
    "DeferredStructuredItem",
    "EvidenceTreeStructuringResult",
    "EvidenceTreeStructuringResultID",
    "EvidenceTree",
    "EvidenceTreeBuildResult",
    "EvidenceTreeID",
    "EvidenceTreeNode",
    "EvidenceTreeNodeID",
    "EvidenceTreeNodeOrigin",
    "EvidenceTreeNodeType",
    "EvidenceTreeRelationType",
    "InputID",
    "ItemEvidenceTreeLink",
    "ItemID",
    "NegationStatus",
    "SpanID",
    "StageID",
    "TemporalRelation",
    "ValidationSeverity",
]


def __getattr__(name: str) -> object:
    """Lazily import public schema classes."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return public names for interactive discovery."""
    return sorted(set(globals()) | set(__all__))
