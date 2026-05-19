"""Evidence Relation Extractor — LLM #3 of the Evidence Graph Structurer.

Produces RelationCandidate dicts (not yet final EvidenceRelations — the
graph composer assigns canonical relation_ids and rewrites refs to the
actual node ids it minted). The LLM works per item, knows about that item's
ClinicalObjectAssertions and EvidenceFrames, and emits typed links between
them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

from src.schemas.case_structurer.common import ConfidenceLevel
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_frame import EvidenceFrame
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)
from src.schemas.evidence_graph_structurer.evidence_relation import (
    EvidenceBasis,
    EvidenceRefType,
    EvidenceRelationType,
)

from ..prompting import (
    assertion_issue_fields,
    clinical_object_assertion_fields,
    evidence_frame_fields,
    evidence_relation_fields,
    evidence_relation_output_skeleton,
    format_clinical_object_assertions,
    format_evidence_frames,
    format_forbidden_downstream_objects,
    format_graph_structuring_boundary,
    format_item_context,
)
from .base_llm_extractor import BaseLLMExtractor
from .item_context import ItemContext

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


@dataclass(frozen=True)
class RelationCandidate:
    """One LLM-proposed typed link between assertions and/or frames."""

    source_item_id: str
    source_ref: str
    source_ref_type: EvidenceRefType
    relation_type: EvidenceRelationType
    target_ref: str
    target_ref_type: EvidenceRefType
    evidence_basis: EvidenceBasis
    confidence: ConfidenceLevel
    source_span_ids: tuple[str, ...] = field(default_factory=tuple)
    notes: str | None = None


_INSTRUCTION = (
    "Extract typed semantic relations between the provided ClinicalObjectAssertions "
    "and/or EvidenceFrames for one StructuredClinicalItem. Each relation_type must "
    "come from the closed EvidenceRelationType vocabulary. Each endpoint must be an "
    "id from the provided lists (assertion object_id for node endpoints, frame_id "
    "for frame endpoints). Do not invent ids. Do not output diagnoses, hypotheses, "
    "treatments, or any other downstream reasoning objects."
)


class EvidenceRelationExtractor:
    """LLM-driven relation extractor over assertions and frames of one item."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "evidence_graph_structurer",
    ) -> None:
        self.extractor = BaseLLMExtractor(llm_client, agent_name=agent_name)

    def extract(
        self,
        contexts: list[ItemContext],
        assertions_by_item: dict[str, list[ClinicalObjectAssertion]],
        frames_by_item: dict[str, list[EvidenceFrame]],
    ) -> tuple[list[RelationCandidate], list[EvidenceStructuringIssue]]:
        candidates: list[RelationCandidate] = []
        issues: list[EvidenceStructuringIssue] = []
        for context in contexts:
            item_assertions = assertions_by_item.get(context.item_id, [])
            if not item_assertions:
                continue
            item_frames = frames_by_item.get(context.item_id, [])
            item_candidates, item_issues = self._extract_one(
                context, item_assertions, item_frames
            )
            candidates.extend(item_candidates)
            issues.extend(item_issues)
        return candidates, issues

    def _extract_one(
        self,
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
        frames: list[EvidenceFrame],
    ) -> tuple[list[RelationCandidate], list[EvidenceStructuringIssue]]:
        prompt_path = self.extractor.prompt_path("evidence_relation_extraction")
        template_vars = {
            "graph_structuring_boundary": format_graph_structuring_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "item_context": format_item_context(context),
            "clinical_object_assertion_fields": clinical_object_assertion_fields(),
            "evidence_frame_fields": evidence_frame_fields(),
            "evidence_relation_fields": evidence_relation_fields(),
            "assertion_issue_fields": assertion_issue_fields(),
            "evidence_relation_output_skeleton": evidence_relation_output_skeleton(),
            "clinical_object_assertions": format_clinical_object_assertions(assertions),
            "evidence_frames": format_evidence_frames(frames),
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
            "evidence_frames": [
                {
                    "frame_id": f.frame_id,
                    "frame_type": f.frame_type.value,
                    "frame_label": f.frame_label,
                    "member_assertion_ids": list(f.member_assertion_ids),
                }
                for f in frames
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
                    code="evidence_relation_llm_invalid_json",
                    message=(
                        "LLM returned non-JSON content for evidence relation "
                        f"extraction: {exc.msg}"
                    ),
                    related_item_id=context.item_id,
                )
            ]
        except Exception as exc:
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_relation_llm_failed",
                    message=(
                        f"Evidence relation LLM call failed: "
                        f"{type(exc).__name__}: {exc}"
                    ),
                    related_item_id=context.item_id,
                )
            ]

        return self._coerce_candidates(context, assertions, frames, payload)

    @staticmethod
    def _coerce_candidates(
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
        frames: list[EvidenceFrame],
        payload: Any,
    ) -> tuple[list[RelationCandidate], list[EvidenceStructuringIssue]]:
        issues: list[EvidenceStructuringIssue] = []
        if not isinstance(payload, dict):
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_relation_payload_invalid",
                    message="Relation payload is not a JSON object.",
                    related_item_id=context.item_id,
                )
            ]
        raw_relations = payload.get("evidence_relations")
        if not isinstance(raw_relations, list):
            return [], [
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="evidence_relation_payload_missing",
                    message="Relation payload missing 'evidence_relations' list.",
                    related_item_id=context.item_id,
                )
            ]

        valid_assertion_ids = {a.object_id for a in assertions}
        valid_frame_ids = {f.frame_id for f in frames}
        valid_span_ids = set(context.span_ids)

        candidates: list[RelationCandidate] = []
        for index, raw in enumerate(raw_relations):
            if not isinstance(raw, dict):
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_invalid_shape",
                        message=f"Relation #{index} dropped: not a JSON object.",
                        related_item_id=context.item_id,
                    )
                )
                continue

            source_ref = _str(raw.get("source_ref"))
            target_ref = _str(raw.get("target_ref"))
            if not source_ref or not target_ref:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_missing_endpoint",
                        message=f"Relation #{index} dropped: missing endpoint id.",
                        related_item_id=context.item_id,
                    )
                )
                continue

            source_ref_type = _enum(
                raw.get("source_ref_type"),
                EvidenceRefType,
                default=EvidenceRefType.NODE,
            )
            target_ref_type = _enum(
                raw.get("target_ref_type"),
                EvidenceRefType,
                default=EvidenceRefType.NODE,
            )

            if not _endpoint_known(
                source_ref, source_ref_type, valid_assertion_ids, valid_frame_ids
            ):
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_unknown_source",
                        message=(
                            f"Relation #{index} dropped: unknown source endpoint "
                            f"{source_ref!r}."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue
            if not _endpoint_known(
                target_ref, target_ref_type, valid_assertion_ids, valid_frame_ids
            ):
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_unknown_target",
                        message=(
                            f"Relation #{index} dropped: unknown target endpoint "
                            f"{target_ref!r}."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue

            relation_type_raw = raw.get("relation_type")
            relation_type = _enum(relation_type_raw, EvidenceRelationType, default=None)
            if relation_type is None:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_unknown_type",
                        message=(
                            f"Relation #{index} dropped: unknown relation_type "
                            f"{relation_type_raw!r}."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue

            evidence_basis = _enum(
                raw.get("evidence_basis"),
                EvidenceBasis,
                default=EvidenceBasis.SOURCE_TEXT,
            )
            confidence = _enum(
                raw.get("confidence"),
                ConfidenceLevel,
                default=ConfidenceLevel.MEDIUM,
            )

            span_ids_raw = raw.get("source_span_ids") or []
            span_ids: list[str] = []
            if isinstance(span_ids_raw, list):
                for sid in span_ids_raw:
                    sid_s = _str(sid)
                    if sid_s is None or sid_s not in valid_span_ids or sid_s in span_ids:
                        continue
                    span_ids.append(sid_s)

            notes = _optional_str(raw.get("notes"))

            candidates.append(
                RelationCandidate(
                    source_item_id=context.item_id,
                    source_ref=source_ref,
                    source_ref_type=source_ref_type,
                    relation_type=relation_type,
                    target_ref=target_ref,
                    target_ref_type=target_ref_type,
                    evidence_basis=evidence_basis,
                    confidence=confidence,
                    source_span_ids=tuple(span_ids),
                    notes=notes,
                )
            )

        return candidates, issues


def _endpoint_known(
    ref: str,
    ref_type: EvidenceRefType,
    valid_assertion_ids: set[str],
    valid_frame_ids: set[str],
) -> bool:
    if ref_type is EvidenceRefType.NODE:
        return ref in valid_assertion_ids
    if ref_type is EvidenceRefType.FRAME:
        return ref in valid_frame_ids
    return False


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
