"""Evidence Frame Assembler — LLM #2 of the Evidence Graph Structurer.

For each ItemContext together with its resolved ClinicalObjectAssertions,
the LLM groups assertions into one or more EvidenceFrames. The validator
keeps only frames whose members are real assertion ids of this item.
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from src.schemas.case_structurer.common import ConfidenceLevel
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_frame import (
    EvidenceFrame,
    EvidenceFrameType,
)
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)

from ..prompting import (
    assertion_issue_fields,
    clinical_object_assertion_fields,
    evidence_frame_fields,
    evidence_frame_output_skeleton,
    format_clinical_object_assertions,
    format_forbidden_downstream_objects,
    format_graph_structuring_boundary,
    format_item_context,
)
from .base_llm_extractor import BaseLLMExtractor
from .item_context import ItemContext

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


_INSTRUCTION = (
    "Group the provided ClinicalObjectAssertions for one StructuredClinicalItem "
    "into source-grounded EvidenceFrames. Each frame must reference real "
    "assertion ids from the input list via member_assertion_ids and must use a "
    "frame_type from the closed EvidenceFrameType vocabulary. Do not invent "
    "parent/child links between assertions; frame grouping is the only allowed "
    "structure. Do not output diagnoses, hypotheses, treatments, or any other "
    "downstream reasoning objects."
)


class EvidenceFrameAssembler:
    """LLM-driven frame assembler over assertions of a single item."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "evidence_graph_structurer",
    ) -> None:
        self.extractor = BaseLLMExtractor(llm_client, agent_name=agent_name)

    def assemble(
        self,
        contexts: list[ItemContext],
        assertions_by_item: dict[str, list[ClinicalObjectAssertion]],
    ) -> tuple[list[EvidenceFrame], list[EvidenceStructuringIssue]]:
        frames: list[EvidenceFrame] = []
        issues: list[EvidenceStructuringIssue] = []
        for context in contexts:
            item_assertions = assertions_by_item.get(context.item_id, [])
            if not item_assertions:
                continue
            item_frames, item_issues = self._assemble_one(context, item_assertions)
            frames.extend(item_frames)
            issues.extend(item_issues)
        return frames, issues

    def _assemble_one(
        self,
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
    ) -> tuple[list[EvidenceFrame], list[EvidenceStructuringIssue]]:
        prompt_path = self.extractor.prompt_path("evidence_frame_assembling")
        template_vars = {
            "graph_structuring_boundary": format_graph_structuring_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "item_context": format_item_context(context),
            "clinical_object_assertion_fields": clinical_object_assertion_fields(),
            "evidence_frame_fields": evidence_frame_fields(),
            "assertion_issue_fields": assertion_issue_fields(),
            "evidence_frame_output_skeleton": evidence_frame_output_skeleton(),
            "clinical_object_assertions": format_clinical_object_assertions(assertions),
        }
        user_payload: dict[str, Any] = {
            "item_id": context.item_id,
            "source_text": context.source_text,
            "clinical_object_assertions": [
                {
                    "object_id": a.object_id,
                    "object_text": a.object_text,
                    "object_type": a.object_type.value,
                    "assertion_status": a.assertion_status.value,
                    "temporal_anchor_text": a.temporal_anchor_text,
                    "trigger_text": a.trigger_text,
                }
                for a in assertions
            ],
        }

        try:
            raw_content = self.extractor.generate_json(
                prompt_path=prompt_path,
                user_payload=user_payload,
                instruction=_INSTRUCTION,
                template_vars=template_vars,
            )
            payload = self.extractor.parse_json_content(raw_content)
        except JSONDecodeError as exc:
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_frame_llm_invalid_json",
                    message=(
                        "LLM returned non-JSON content for evidence frame "
                        f"assembling: {exc.msg}"
                    ),
                    related_item_id=context.item_id,
                )
            ]
        except Exception as exc:  # network/parse safety net
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_frame_llm_failed",
                    message=(
                        f"Evidence frame LLM call failed: {type(exc).__name__}: {exc}"
                    ),
                    related_item_id=context.item_id,
                )
            ]

        return self._coerce_frames(context, assertions, payload)

    @staticmethod
    def _coerce_frames(
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
        payload: Any,
    ) -> tuple[list[EvidenceFrame], list[EvidenceStructuringIssue]]:
        issues: list[EvidenceStructuringIssue] = []
        if not isinstance(payload, dict):
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_frame_payload_invalid",
                    message="Frame payload is not a JSON object.",
                    related_item_id=context.item_id,
                )
            ]
        raw_frames = payload.get("evidence_frames")
        if not isinstance(raw_frames, list):
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_frame_payload_missing",
                    message="Frame payload missing 'evidence_frames' list.",
                    related_item_id=context.item_id,
                )
            ]

        valid_assertion_ids = {a.object_id for a in assertions}
        valid_span_ids = set(context.span_ids)
        frames: list[EvidenceFrame] = []

        for index, raw in enumerate(raw_frames):
            if not isinstance(raw, dict):
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_frame_dropped_invalid_shape",
                        message=f"Frame #{index} dropped: not a JSON object.",
                        related_item_id=context.item_id,
                    )
                )
                continue

            frame_label = _str(raw.get("frame_label"))
            if not frame_label:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_frame_dropped_missing_label",
                        message=f"Frame #{index} dropped: missing frame_label.",
                        related_item_id=context.item_id,
                    )
                )
                continue

            frame_type = _enum(
                raw.get("frame_type"),
                EvidenceFrameType,
                default=EvidenceFrameType.UNCERTAIN_OTHER,
            )

            member_ids_raw = raw.get("member_assertion_ids") or []
            member_ids: list[str] = []
            if isinstance(member_ids_raw, list):
                for mid in member_ids_raw:
                    mid_s = _str(mid)
                    if mid_s is None:
                        continue
                    if mid_s not in valid_assertion_ids:
                        continue
                    if mid_s in member_ids:
                        continue
                    member_ids.append(mid_s)

            span_ids_raw = raw.get("source_span_ids") or []
            span_ids: list[str] = []
            if isinstance(span_ids_raw, list):
                for sid in span_ids_raw:
                    sid_s = _str(sid)
                    if sid_s is None or sid_s not in valid_span_ids or sid_s in span_ids:
                        continue
                    span_ids.append(sid_s)
            if not span_ids and context.span_ids:
                span_ids = list(context.span_ids)

            confidence = _enum(
                raw.get("confidence"),
                ConfidenceLevel,
                default=ConfidenceLevel.MEDIUM,
            )
            notes = _optional_str(raw.get("notes"))

            try:
                frame = EvidenceFrame(
                    source_item_id=context.item_id,
                    frame_type=frame_type,
                    frame_label=frame_label,
                    member_assertion_ids=member_ids,
                    source_span_ids=span_ids,
                    confidence=confidence,
                    notes=notes,
                )
            except ValidationError as exc:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_frame_dropped_invalid",
                        message=f"Frame #{index} dropped: {exc.errors()[0].get('msg', '?')}",
                        related_item_id=context.item_id,
                    )
                )
                continue
            frames.append(frame)

        for raw_issue in payload.get("frame_issues", []) or []:
            if not isinstance(raw_issue, dict):
                continue
            try:
                issues.append(EvidenceStructuringIssue(**raw_issue))
            except ValidationError:
                continue

        return frames, issues


def _str(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return None


def _optional_str(value: Any) -> str | None:
    return _str(value)


def _enum(value: Any, enum_type: type, default: Any) -> Any:
    if isinstance(value, str):
        try:
            return enum_type(value.strip())
        except ValueError:
            return default
    return default
