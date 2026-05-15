"""Public exports for Evidence Atomizer schemas.

The schema classes are loaded lazily so importing
``src.schemas.evidence_atomizer.common`` from the centralized ID generator does
not create a circular import through model modules.
"""

from __future__ import annotations

from importlib import import_module

from .common import (
    AtomizationTransformationType,
    CaseID,
    CertaintyLevel,
    ClinicalDomain,
    ConfidenceLevel,
    DeferredReason,
    EvidenceAtomizationResultID,
    EvidenceGranularity,
    EvidenceID,
    EvidenceType,
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
    "EvidenceAtom": ".evidence_atom",
    "EvidenceSourceContext": ".evidence_source_context",
    "ItemEvidenceLink": ".item_evidence_link",
    "DeferredStructuredItem": ".deferred_item",
    "AtomizationWarning": ".atomization_warning",
    "EvidenceAtomizationResult": ".evidence_atomization_result",
}

__all__ = [
    "AtomizationTransformationType",
    "AtomizationWarning",
    "CaseID",
    "CertaintyLevel",
    "ClinicalAssertionResolutionResult",
    "ClinicalObjectAssertion",
    "ClinicalObjectAssertionStatus",
    "ClinicalObjectType",
    "ClinicalDomain",
    "ConfidenceLevel",
    "DeferredReason",
    "DeferredStructuredItem",
    "EvidenceAtom",
    "EvidenceAtomizationResult",
    "EvidenceAtomizationResultID",
    "EvidenceSourceContext",
    "EvidenceGranularity",
    "EvidenceID",
    "EvidenceType",
    "InputID",
    "ItemEvidenceLink",
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
