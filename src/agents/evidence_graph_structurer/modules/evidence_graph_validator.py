"""Evidence Graph Validator — deterministic, non-repairing.

For one EvidenceGraphlet, run schema/source/structural checks and produce one
EvidenceGraphValidationReport. The validator does not modify the graphlet.

A graphlet's status is decided by issue severity:
- any ERROR-level issue → REJECTED
- any WARNING-level issue → NEEDS_REVIEW
- otherwise → ACCEPTED
"""

from __future__ import annotations

from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_graph_validation import (
    EvidenceGraphValidationReport,
    EvidenceGraphValidationStatus,
)
from src.schemas.evidence_graph_structurer.evidence_graphlet import EvidenceGraphlet
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)
from src.schemas.evidence_graph_structurer.evidence_relation import (
    EvidenceRefType,
    endpoint_kind,
    is_endpoint_allowed,
)

from .item_context import ItemContext


class EvidenceGraphValidator:
    """Validate one EvidenceGraphlet against its source item context."""

    def validate(
        self,
        context: ItemContext,
        graphlet: EvidenceGraphlet,
        assertions: list[ClinicalObjectAssertion],
    ) -> EvidenceGraphValidationReport:
        issues: list[EvidenceStructuringIssue] = []

        assertion_by_id = {a.object_id: a for a in assertions}
        node_ids = {n.node_id for n in graphlet.nodes}
        frame_ids = {f.frame_id for f in graphlet.frames}
        node_type_by_id = {n.node_id: n.node_type for n in graphlet.nodes}
        frame_type_by_id = {f.frame_id: f.frame_type for f in graphlet.frames}
        valid_span_ids = set(context.span_ids)

        # Node grounding
        for node in graphlet.nodes:
            if context.source_text and node.text not in context.source_text:
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_node_text_not_grounded",
                        message=(
                            f"Node text {node.text!r} is not a substring of "
                            "item source_text."
                        ),
                        related_item_id=context.item_id,
                        related_node_id=node.node_id,
                    )
                )
            for aid in node.assertion_ids:
                if aid not in assertion_by_id:
                    issues.append(
                        EvidenceStructuringIssue(
                            severity=ValidationSeverity.WARNING,
                            code="evidence_node_unknown_assertion",
                            message=(
                                f"Node references unknown assertion id {aid!r}."
                            ),
                            related_item_id=context.item_id,
                            related_node_id=node.node_id,
                            related_assertion_id=aid,
                        )
                    )
            for sid in node.source_span_ids:
                if sid not in valid_span_ids:
                    issues.append(
                        EvidenceStructuringIssue(
                            severity=ValidationSeverity.WARNING,
                            code="evidence_node_unknown_span",
                            message=(
                                f"Node references unknown source span id {sid!r}."
                            ),
                            related_item_id=context.item_id,
                            related_node_id=node.node_id,
                            related_span_id=sid,
                        )
                    )

        # Frame coverage
        empty_frame_ids: list[str] = []
        for frame in graphlet.frames:
            if not frame.member_assertion_ids and not frame.member_node_ids:
                empty_frame_ids.append(frame.frame_id)
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_frame_empty",
                        message=(
                            f"Frame {frame.frame_id!r} has no assertion or node "
                            "members."
                        ),
                        related_item_id=context.item_id,
                        related_frame_id=frame.frame_id,
                    )
                )
            for aid in frame.member_assertion_ids:
                if aid not in assertion_by_id:
                    issues.append(
                        EvidenceStructuringIssue(
                            severity=ValidationSeverity.WARNING,
                            code="evidence_frame_unknown_assertion",
                            message=(
                                f"Frame references unknown assertion id {aid!r}."
                            ),
                            related_item_id=context.item_id,
                            related_frame_id=frame.frame_id,
                            related_assertion_id=aid,
                        )
                    )
            for nid in frame.member_node_ids:
                if nid not in node_ids:
                    issues.append(
                        EvidenceStructuringIssue(
                            severity=ValidationSeverity.WARNING,
                            code="evidence_frame_unknown_node",
                            message=(
                                f"Frame references unknown node id {nid!r}."
                            ),
                            related_item_id=context.item_id,
                            related_frame_id=frame.frame_id,
                            related_node_id=nid,
                        )
                    )

        # Relation endpoint checks
        invalid_endpoint_count = 0
        incompatible_endpoint_count = 0
        for relation in graphlet.relations:
            source_known = _endpoint_known(
                relation.source_ref, relation.source_ref_type, node_ids, frame_ids
            )
            target_known = _endpoint_known(
                relation.target_ref, relation.target_ref_type, node_ids, frame_ids
            )
            if not source_known or not target_known:
                invalid_endpoint_count += 1
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_unknown_endpoint",
                        message=(
                            "Relation references unknown endpoint: "
                            f"source={relation.source_ref!r} "
                            f"target={relation.target_ref!r}."
                        ),
                        related_item_id=context.item_id,
                        related_relation_id=relation.relation_id,
                    )
                )
                continue

            source_kind = endpoint_kind(
                relation.source_ref_type,
                _ref_type_value(
                    relation.source_ref,
                    relation.source_ref_type,
                    node_type_by_id,
                    frame_type_by_id,
                ),
            )
            target_kind = endpoint_kind(
                relation.target_ref_type,
                _ref_type_value(
                    relation.target_ref,
                    relation.target_ref_type,
                    node_type_by_id,
                    frame_type_by_id,
                ),
            )

            allowed_source = is_endpoint_allowed(
                relation.relation_type, "source", source_kind
            )
            allowed_target = is_endpoint_allowed(
                relation.relation_type, "target", target_kind
            )
            if not allowed_source or not allowed_target:
                incompatible_endpoint_count += 1
                issues.append(
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_relation_endpoint_incompatible",
                        message=(
                            "Relation endpoint kinds incompatible with "
                            f"relation_type={relation.relation_type.value!r}: "
                            f"source_kind={source_kind!r}, target_kind={target_kind!r}."
                        ),
                        related_item_id=context.item_id,
                        related_relation_id=relation.relation_id,
                    )
                )

        # Assertion coverage
        covered_assertion_ids: set[str] = set()
        for node in graphlet.nodes:
            for aid in node.assertion_ids:
                if aid in assertion_by_id:
                    covered_assertion_ids.add(aid)
        uncovered = [
            aid for aid in assertion_by_id if aid not in covered_assertion_ids
        ]
        if uncovered:
            issues.append(
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.WARNING,
                    code="evidence_graph_assertion_uncovered",
                    message=(
                        "Some assertions are not covered by any node: "
                        f"{uncovered}."
                    ),
                    related_item_id=context.item_id,
                )
            )

        has_error = any(
            issue.severity is ValidationSeverity.ERROR for issue in issues
        )
        has_warning = any(
            issue.severity is ValidationSeverity.WARNING for issue in issues
        )
        if has_error:
            status = EvidenceGraphValidationStatus.REJECTED
        elif has_warning:
            status = EvidenceGraphValidationStatus.NEEDS_REVIEW
        else:
            status = EvidenceGraphValidationStatus.ACCEPTED

        report = EvidenceGraphValidationReport(
            source_item_id=context.item_id,
            graphlet_id=graphlet.graphlet_id,
            status=status,
            issues=issues,
            assertion_coverage={
                "total": len(assertion_by_id),
                "covered": len(covered_assertion_ids),
                "uncovered_assertion_ids": uncovered,
            },
            frame_coverage={
                "total": len(graphlet.frames),
                "empty": len(empty_frame_ids),
                "empty_frame_ids": empty_frame_ids,
            },
            relation_checks={
                "total": len(graphlet.relations),
                "unknown_endpoint": invalid_endpoint_count,
                "incompatible_endpoint": incompatible_endpoint_count,
            },
            downstream_readiness=not has_error,
        )
        return report


def _endpoint_known(
    ref: str,
    ref_type: EvidenceRefType,
    node_ids: set[str],
    frame_ids: set[str],
) -> bool:
    if ref_type is EvidenceRefType.NODE:
        return ref in node_ids
    if ref_type is EvidenceRefType.FRAME:
        return ref in frame_ids
    return False


def _ref_type_value(
    ref: str,
    ref_type: EvidenceRefType,
    node_type_by_id: dict[str, object],
    frame_type_by_id: dict[str, object],
) -> str | None:
    if ref_type is EvidenceRefType.NODE:
        value = node_type_by_id.get(ref)
    elif ref_type is EvidenceRefType.FRAME:
        value = frame_type_by_id.get(ref)
    else:
        value = None
    if value is None:
        return None
    return getattr(value, "value", str(value))
