"""Shared primitive types for Attribute Extractor schemas."""

from __future__ import annotations

from typing import TypeAlias

from src.schemas.case_structurer.common import (
    CaseID,
    CaseStructuringResultID,
    ConfidenceLevel,
    InputID,
    ItemID,
    SpanID,
    ValidationSeverity,
)

AttributeID: TypeAlias = str
AttributeExtractionResultID: TypeAlias = str

__all__ = [
    "AttributeExtractionResultID",
    "AttributeID",
    "CaseID",
    "CaseStructuringResultID",
    "ConfidenceLevel",
    "InputID",
    "ItemID",
    "SpanID",
    "ValidationSeverity",
]
