from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Any

from src.schemas.case_structurer.ambiguity_item import AmbiguityType
from src.schemas.case_structurer.clinical_section import ClinicalSectionType
from src.schemas.case_structurer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
    TimeExpressionType,
)
from src.schemas.case_structurer.stage_context import StageRelation, StageType
from src.schemas.case_structurer.structured_clinical_item import ClinicalItemType
from src.schemas.case_structurer.timeline_event import TimelineEventType


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    """Return schema enum values in declaration order."""
    return [item.value for item in enum_cls]


def format_enum_values(values: Iterable[str]) -> str:
    """Format enum values as a compact prompt-friendly bullet list."""
    value_list = list(values)
    if not value_list:
        return "(none)"
    return "\n".join(f"- {value}" for value in value_list)


def stage_context_contract() -> dict[str, Any]:
    return {
        "allowed_stage_type_values": format_enum_values(enum_values(StageType)),
        "allowed_relation_values": format_enum_values(enum_values(StageRelation)),
        "allowed_confidence_values": format_enum_values(enum_values(ConfidenceLevel)),
        "stage_type_default_value": StageType.UNKNOWN.value,
        "relation_initial_value": StageRelation.NEW_CASE_START.value,
        "relation_default_value": StageRelation.UNKNOWN.value,
    }


def clinical_section_contract() -> dict[str, Any]:
    return {
        "allowed_section_type_values": format_enum_values(
            enum_values(ClinicalSectionType)
        ),
        "allowed_confidence_values": format_enum_values(enum_values(ConfidenceLevel)),
    }


def structured_item_contract() -> dict[str, Any]:
    return {
        "allowed_item_type_values": format_enum_values(enum_values(ClinicalItemType)),
        "allowed_temporality_values": format_enum_values(
            enum_values(TemporalRelation)
        ),
        "allowed_certainty_values": format_enum_values(enum_values(CertaintyLevel)),
        "allowed_negation_values": format_enum_values(enum_values(NegationStatus)),
        "allowed_confidence_values": format_enum_values(enum_values(ConfidenceLevel)),
        "example_primary_item_type_value": ClinicalItemType.SYMPTOM.value,
        "example_duration_temporality_value": TemporalRelation.CHRONIC.value,
        "example_change_temporality_value": TemporalRelation.RECENT_WORSENING.value,
    }


def temporal_ambiguity_contract() -> dict[str, Any]:
    return {
        "allowed_event_type_values": format_enum_values(
            enum_values(TimelineEventType)
        ),
        "allowed_time_expression_type_values": format_enum_values(
            enum_values(TimeExpressionType)
        ),
        "allowed_ambiguity_type_values": format_enum_values(enum_values(AmbiguityType)),
        "allowed_confidence_values": format_enum_values(enum_values(ConfidenceLevel)),
        "example_source_uncertainty_type_value": (
            AmbiguityType.UNCLEAR_DIAGNOSIS_STATUS.value
        ),
    }
