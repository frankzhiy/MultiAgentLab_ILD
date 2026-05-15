"""Public exports for Attribute Extractor schemas."""

from __future__ import annotations

from importlib import import_module

from .attribute_role import AttributeRole
from .common import (
    AttributeExtractionResultID,
    AttributeID,
    CaseID,
    CaseStructuringResultID,
    ConfidenceLevel,
    InputID,
    ItemID,
    SpanID,
    ValidationSeverity,
)

_LAZY_EXPORTS = {
    "ClinicalAttribute": ".clinical_attribute",
    "AttributeExtractionResult": ".attribute_extraction_result",
    "AttributeExtractionWarning": ".attribute_extraction_result",
}

__all__ = [
    "AttributeExtractionResult",
    "AttributeExtractionResultID",
    "AttributeExtractionWarning",
    "AttributeID",
    "AttributeRole",
    "CaseID",
    "CaseStructuringResultID",
    "ClinicalAttribute",
    "ConfidenceLevel",
    "InputID",
    "ItemID",
    "SpanID",
    "ValidationSeverity",
]


def __getattr__(name: str) -> object:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
