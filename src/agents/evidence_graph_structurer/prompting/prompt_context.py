"""Prompt-context formatters shared by Evidence Graph Structurer LLM calls."""

from __future__ import annotations

from src.agents.evidence_graph_structurer.modules.item_context import ItemContext
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.evidence_frame import EvidenceFrame


def format_item_context(context: ItemContext) -> str:
    """Render one ItemContext as a flat key=value block for the prompt."""

    span_text = "; ".join(
        f"{span.get('span_id')}: {_compact(str(span.get('quoted_text', '')))}"
        for span in context.spans
    )
    lines = [
        f"item_id={context.item_id}",
        f"item_type={context.item_type}",
        f"label={_compact(context.label)}",
        f"temporality={context.temporality}",
        f"certainty={context.certainty}",
        f"negation={context.negation}",
        f"section_id={context.section_id}",
        f"section_type={context.section_type}",
        f"section_title={context.section_title}",
        f"source_spans=[{span_text}]",
        f"source_text={_compact(context.source_text, limit=400)}",
    ]
    return "- " + " | ".join(lines)


def format_clinical_object_assertions(
    assertions: list[ClinicalObjectAssertion],
) -> str:
    if not assertions:
        return "(no assertions)"

    lines: list[str] = []
    for index, assertion in enumerate(assertions, start=1):
        modifiers = (
            ", ".join(assertion.modifier_texts) if assertion.modifier_texts else "-"
        )
        lines.append(
            " | ".join(
                [
                    f"#{index}",
                    f"object_id={assertion.object_id}",
                    f"object_text={_compact(assertion.object_text)}",
                    f"object_type={assertion.object_type.value}",
                    f"assertion_status={assertion.assertion_status.value}",
                    f"temporal_anchor_text={assertion.temporal_anchor_text or '-'}",
                    f"trigger_text={assertion.trigger_text or '-'}",
                    f"modifier_texts=[{modifiers}]",
                    f"cue={assertion.assertion_cue_text or '-'}",
                    f"scope={assertion.assertion_scope_text or '-'}",
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def format_evidence_frames(frames: list[EvidenceFrame]) -> str:
    if not frames:
        return "(no frames)"

    lines: list[str] = []
    for index, frame in enumerate(frames, start=1):
        members = (
            ", ".join(frame.member_assertion_ids)
            if frame.member_assertion_ids
            else "-"
        )
        lines.append(
            " | ".join(
                [
                    f"#{index}",
                    f"frame_id={frame.frame_id}",
                    f"frame_type={frame.frame_type.value}",
                    f"frame_label={_compact(frame.frame_label)}",
                    f"member_assertion_ids=[{members}]",
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def format_graph_structuring_boundary() -> str:
    return "\n".join(
        [
            "- Evidence Graph Structurer receives validated StructuredClinicalItem material.",
            "- It first resolves source-grounded clinical object assertions (each assertion carries only its own intrinsic information: object, status, cue, scope, temporal_anchor, trigger, modifiers).",
            "- It then assembles EvidenceFrames (semantic groups of assertions and nodes) and extracts typed EvidenceRelations between nodes and frames.",
            "- The final structure is a per-item EvidenceGraphlet (frames + nodes + relations); there is NO parent_node_id and NO relation_to_parent.",
            "- It does not decide disease support, refutation, diagnosis, treatment, or any downstream action.",
            "- It does not generate hypothesis material.",
        ]
    )


def format_forbidden_downstream_objects() -> str:
    forbidden = [
        "diagnosis selection",
        "diagnostic hypothesis",
        "support/refute relationship",
        "treatment recommendation",
        "ActionPlan",
        "HypothesisState",
        "Conflict",
        "UpdateTrace",
        "ArbitrationResult",
        "SafetyGateResult",
        "StateWriter output",
    ]
    return "\n".join(f"- {item}" for item in forbidden)


def format_relation_candidates(candidates: list[dict[str, object]]) -> str:
    if not candidates:
        return "(no candidates)"
    lines: list[str] = []
    for index, cand in enumerate(candidates, start=1):
        lines.append(
            " | ".join(
                [
                    f"#{index}",
                    f"source_ref={cand.get('source_ref', '-')}",
                    f"source_ref_type={cand.get('source_ref_type', '-')}",
                    f"relation_type={cand.get('relation_type', '-')}",
                    f"target_ref={cand.get('target_ref', '-')}",
                    f"target_ref_type={cand.get('target_ref_type', '-')}",
                ]
            )
        )
    return "\n".join(f"- {line}" for line in lines)


def _compact(text: str, limit: int = 160) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return f"{compacted[: limit - 3]}..."
