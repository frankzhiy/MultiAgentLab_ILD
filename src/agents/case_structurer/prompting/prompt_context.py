from __future__ import annotations

from enum import StrEnum
from typing import Any

from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import StageContext
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem


def format_forbidden_objects() -> str:
    forbidden = [
        "final diagnosis",
        "differential diagnosis",
        "treatment recommendation",
        "management plan",
        "EvidenceAtom",
        "HypothesisState",
        "Conflict",
        "ActionPlan",
        "UpdateTrace",
        "ArbitrationResult",
        "SafetyGateResult",
    ]
    return "\n".join(f"- {item}" for item in forbidden)


def format_source_span_policy(input_id: str) -> str:
    return "\n".join(
        [
            "- Every extracted object must include source_spans.",
            f"- source_spans[*].input_id must equal {input_id}.",
            (
                "- quoted_text must be copied from raw_text or be a near-exact "
                "source fragment."
            ),
            "- Set char_start and char_end to null unless you are certain.",
            "- Code will resolve exact offsets later.",
            "- Never invent source text.",
        ]
    )


def format_raw_input_summary(raw_input: RawTextInput) -> str:
    return "\n".join(
        [
            f"input_id: {raw_input.input_id}",
            f"case_id: {raw_input.case_id}",
            f"input_order: {raw_input.input_order}",
            f"parent_input_id: {raw_input.parent_input_id}",
            f"raw_text_chars: {len(raw_input.raw_text)}",
            f"raw_text_preview: {_compact_text(raw_input.raw_text, limit=240)}",
        ]
    )


def format_stage_context_summary(stage_context: StageContext) -> str:
    basis = stage_context.classification_basis or "None"
    return "\n".join(
        [
            f"stage_id: {stage_context.stage_id}",
            f"case_id: {stage_context.case_id}",
            f"input_id: {stage_context.input_id}",
            f"stage_order: {stage_context.stage_order}",
            f"stage_type: {_value(stage_context.stage_type)}",
            (
                "relation_to_previous_stage: "
                f"{_value(stage_context.relation_to_previous_stage)}"
            ),
            f"is_initial_stage: {stage_context.is_initial_stage}",
            (
                "classification_confidence: "
                f"{_value(stage_context.classification_confidence)}"
            ),
            f"classification_basis: {basis}",
        ]
    )


def format_available_sections(sections: list[ClinicalSection]) -> str:
    if not sections:
        return "(none)"

    lines = []
    for section in sections:
        lines.append(
            " | ".join(
                [
                    section.section_id,
                    _value(section.section_type),
                    _compact_text(section.normalized_text),
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def format_available_items(items: list[StructuredClinicalItem]) -> str:
    if not items:
        return "(none)"

    lines = []
    for item in items:
        time_text = item.time_text if item.time_text is not None else "None"
        lines.append(
            " | ".join(
                [
                    item.item_id,
                    item.section_id,
                    _value(item.item_type),
                    _compact_text(item.label),
                    f"time_text={time_text}",
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def _value(value: Any) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


def _compact_text(text: str, limit: int = 120) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return f"{compacted[: limit - 3]}..."
