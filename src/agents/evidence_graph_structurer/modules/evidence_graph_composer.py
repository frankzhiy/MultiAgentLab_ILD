"""Evidence Graph Composer — deterministic, no LLM.

Builds one EvidenceGraphlet per item out of:
  - the item's ClinicalObjectAssertions,
  - the item's EvidenceFrames,
  - the LLM-proposed RelationCandidates.

Each ClinicalObjectAssertion becomes exactly one EvidenceNode of type
CLINICAL_OBJECT. Composite or compound source phrases are NOT materialized
as nodes here — the frame layer is responsible for those.
"""

from __future__ import annotations

from typing import Iterable

from src.schemas.case_structurer.common import ConfidenceLevel
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_frame import EvidenceFrame
from src.schemas.evidence_graph_structurer.evidence_graphlet import (
    EvidenceGraphlet,
    EvidenceGraphletStatus,
)
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)
from src.schemas.evidence_graph_structurer.evidence_node import (
    EvidenceNode,
    EvidenceNodeType,
)
from src.schemas.evidence_graph_structurer.evidence_relation import (
    EvidenceRefType,
    EvidenceRelation,
)

from .evidence_relation_extractor import RelationCandidate
from .item_context import ItemContext


class EvidenceGraphComposer:
    """Deterministic composition of frames + nodes + relations into graphlets."""

    def compose(
        self,
        contexts: list[ItemContext],
        assertions_by_item: dict[str, list[ClinicalObjectAssertion]],
        frames_by_item: dict[str, list[EvidenceFrame]],
        candidates_by_item: dict[str, list[RelationCandidate]],
    ) -> tuple[list[EvidenceGraphlet], list[EvidenceStructuringIssue]]:
        graphlets: list[EvidenceGraphlet] = []
        issues: list[EvidenceStructuringIssue] = []
        for context in contexts:
            item_assertions = assertions_by_item.get(context.item_id, [])
            if not item_assertions:
                continue
            item_frames = frames_by_item.get(context.item_id, [])
            item_candidates = candidates_by_item.get(context.item_id, [])
            graphlet, item_issues = self._compose_one(
                context, item_assertions, item_frames, item_candidates
            )
            graphlets.append(graphlet)
            issues.extend(item_issues)
        return graphlets, issues

    @staticmethod
    def _compose_one(
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
        frames: list[EvidenceFrame],
        candidates: list[RelationCandidate],
    ) -> tuple[EvidenceGraphlet, list[EvidenceStructuringIssue]]:
        issues: list[EvidenceStructuringIssue] = []

        # 1) Build one EvidenceNode per assertion, indexed by assertion id.
        nodes: list[EvidenceNode] = []
        node_id_by_assertion: dict[str, str] = {}
        for assertion in assertions:
            node = EvidenceNode(
                source_item_id=context.item_id,
                node_type=EvidenceNodeType.CLINICAL_OBJECT,
                text=assertion.object_text,
                assertion_ids=[assertion.object_id],
                assertion_status=assertion.assertion_status,
                source_span_ids=list(assertion.source_span_ids),
                confidence=assertion.confidence,
            )
            nodes.append(node)
            node_id_by_assertion[assertion.object_id] = node.node_id

        # 2) Rewrite each frame's member_node_ids to refer to the minted node ids.
        rewritten_frames: list[EvidenceFrame] = []
        for frame in frames:
            member_node_ids = [
                node_id_by_assertion[aid]
                for aid in frame.member_assertion_ids
                if aid in node_id_by_assertion
            ]
            rewritten = frame.model_copy(update={"member_node_ids": member_node_ids})
            rewritten_frames.append(rewritten)

        valid_frame_ids = {f.frame_id for f in rewritten_frames}

        # 3) Materialize EvidenceRelations from candidates by mapping assertion ids
        #    onto node ids.
        relations: list[EvidenceRelation] = []
        seen_relation_keys: set[tuple[str, str, str, str, str]] = set()
        for candidate in candidates:
            mapped = _map_endpoint(
                candidate.source_ref,
                candidate.source_ref_type,
                node_id_by_assertion,
                valid_frame_ids,
            )
            if mapped is None:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_unmapped_source",
                        message=(
                            "Relation dropped: source endpoint could not be mapped "
                            f"to a node or frame ({candidate.source_ref!r})."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue
            source_ref, source_ref_type = mapped

            mapped_target = _map_endpoint(
                candidate.target_ref,
                candidate.target_ref_type,
                node_id_by_assertion,
                valid_frame_ids,
            )
            if mapped_target is None:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_dropped_unmapped_target",
                        message=(
                            "Relation dropped: target endpoint could not be mapped "
                            f"to a node or frame ({candidate.target_ref!r})."
                        ),
                        related_item_id=context.item_id,
                    )
                )
                continue
            target_ref, target_ref_type = mapped_target

            key = (
                source_ref,
                source_ref_type.value,
                candidate.relation_type.value,
                target_ref,
                target_ref_type.value,
            )
            if key in seen_relation_keys:
                continue
            seen_relation_keys.add(key)

            relation = EvidenceRelation(
                source_ref=source_ref,
                source_ref_type=source_ref_type,
                relation_type=candidate.relation_type,
                target_ref=target_ref,
                target_ref_type=target_ref_type,
                evidence_basis=candidate.evidence_basis,
                confidence=candidate.confidence,
                source_span_ids=list(candidate.source_span_ids),
                notes=candidate.notes,
            )
            relations.append(relation)

        display_hints: dict[str, object] = {
            "render_mode": "tree_like",
            "frame_count": len(rewritten_frames),
            "node_count": len(nodes),
            "relation_count": len(relations),
        }

        graphlet = EvidenceGraphlet(
            source_item_id=context.item_id,
            source_span_ids=list(context.span_ids),
            frames=rewritten_frames,
            nodes=nodes,
            relations=relations,
            status=EvidenceGraphletStatus.NEEDS_REVIEW,
            display_hints=display_hints,
        )
        return graphlet, issues


def _map_endpoint(
    ref: str,
    ref_type: EvidenceRefType,
    node_id_by_assertion: dict[str, str],
    valid_frame_ids: Iterable[str],
) -> tuple[str, EvidenceRefType] | None:
    if ref_type is EvidenceRefType.NODE:
        node_id = node_id_by_assertion.get(ref)
        if node_id is None:
            return None
        return node_id, EvidenceRefType.NODE
    if ref_type is EvidenceRefType.FRAME:
        if ref not in set(valid_frame_ids):
            return None
        return ref, EvidenceRefType.FRAME
    return None
