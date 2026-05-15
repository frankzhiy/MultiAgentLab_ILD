from __future__ import annotations

from collections import defaultdict

from src.schemas.evidence_atomizer import AtomizationWarning
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_atomizer.common import ValidationSeverity
from src.schemas.evidence_atomizer.evidence_event_frame import (
    AtomizationPolicy,
    ContextRole,
    EvidenceEventFrame,
    EvidenceFrameNode,
    FrameNodeType,
)

from .atomization_candidate_builder import AtomizationCandidate
from .coverage_units import CoverageUnit, CoverageUnitBuildResult


class FrameAwareCoverageUnitBuilder:
    """Build context-complete coverage units from EvidenceEventFrame nodes."""

    def build(
        self,
        *,
        candidates: list[AtomizationCandidate],
        assertions: list[ClinicalObjectAssertion] | None = None,
        frames: list[EvidenceEventFrame],
    ) -> CoverageUnitBuildResult:
        warnings: list[AtomizationWarning] = []
        coverage_units: list[CoverageUnit] = []
        frames_by_item_id = {frame.source_item_id: frame for frame in frames}
        assertions_by_item_id: dict[str, list[ClinicalObjectAssertion]] = defaultdict(list)
        for assertion in assertions or []:
            assertions_by_item_id[assertion.source_item_id].append(assertion)

        for candidate in candidates:
            frame = frames_by_item_id.get(candidate.item_id)
            if frame is None:
                warnings.append(
                    _warning(
                        code="frame_missing_for_candidate",
                        message="No EvidenceEventFrame was available for this candidate.",
                        related_item_id=candidate.item_id,
                    )
                )
                continue

            coverage_units.extend(
                self._build_frame_units(
                    candidate=candidate,
                    frame=frame,
                    assertions=assertions_by_item_id.get(candidate.item_id, []),
                    warnings=warnings,
                )
            )

        seen_surface_texts: dict[tuple[str, str], str] = {}
        for unit in coverage_units:
            key = (unit.source_item_id, unit.surface_text)
            if key not in seen_surface_texts:
                seen_surface_texts[key] = unit.unit_id
                continue
            warnings.append(
                _warning(
                    code="duplicate_coverage_unit_surface_text",
                    message="Multiple frame-aware coverage units produced the same surface_text.",
                    related_item_id=unit.source_item_id,
                )
            )

        return CoverageUnitBuildResult(
            coverage_units=coverage_units,
            warnings=warnings,
        )

    def _build_frame_units(
        self,
        *,
        candidate: AtomizationCandidate,
        frame: EvidenceEventFrame,
        assertions: list[ClinicalObjectAssertion],
        warnings: list[AtomizationWarning],
    ) -> list[CoverageUnit]:
        nodes_by_id = {node.frame_node_id: node for node in frame.frame_nodes}
        units: list[CoverageUnit] = []
        unit_index = 1

        for node in frame.frame_nodes:
            if not node.atomizable:
                continue
            if node.atomization_policy in {
                AtomizationPolicy.DO_NOT_GENERATE_CONTEXT_ONLY,
                AtomizationPolicy.DEFER,
            }:
                continue

            context_nodes = _context_nodes(node, nodes_by_id)
            if not context_nodes and node.node_type in {
                FrameNodeType.OBJECT_PROPERTY,
                FrameNodeType.CLINICAL_OBJECT,
                FrameNodeType.NEGATIVE_FINDING,
            }:
                warnings.append(
                    _warning(
                        code="atomizable_node_without_context",
                        message="Atomizable frame node did not provide inherited context.",
                        related_item_id=candidate.item_id,
                    )
                )

            if node.node_type == FrameNodeType.OBJECT_PROPERTY:
                parent = nodes_by_id.get(node.parent_node_id or "")
                if parent is None or parent.node_type != FrameNodeType.CLINICAL_OBJECT:
                    warnings.append(
                        _warning(
                            code="orphan_property_coverage_unit",
                            message="Object-property coverage unit has no clinical-object frame parent.",
                            related_item_id=candidate.item_id,
                        )
                    )

            inherited_context_text = _compose_text(context_nodes)
            surface_text = _compose_surface_text(inherited_context_text, node.node_text)
            if not surface_text:
                surface_text = node.node_text
                warnings.append(
                    _warning(
                        code="context_inheritance_failed",
                        message="Coverage unit context composition failed and fell back to local node_text.",
                        related_item_id=candidate.item_id,
                    )
                )

            assertion = _matching_assertion(node, assertions)
            units.append(
                CoverageUnit(
                    unit_id=f"{candidate.item_id}__frame_unit_{unit_index:03d}",
                    source_item_id=candidate.item_id,
                    source_attribute_ids=_dedupe(
                        [
                            *node.source_attribute_ids,
                            *[
                                attribute_id
                                for context_node in context_nodes
                                for attribute_id in context_node.source_attribute_ids
                            ],
                        ]
                    ),
                    source_span_ids=_dedupe(
                        [
                            *node.source_span_ids,
                            *[
                                span_id
                                for context_node in context_nodes
                                for span_id in context_node.source_span_ids
                            ],
                        ]
                    )
                    or _span_ids(candidate),
                    surface_text=surface_text,
                    clinical_object=_clinical_object_text(node, nodes_by_id),
                    status_or_direction=None,
                    modifier_texts=[
                        context_node.node_text
                        for context_node in context_nodes
                        if context_node.context_role == ContextRole.MODIFIER_CONTEXT
                    ],
                    assertion_status=node.assertion_status.value,
                    certainty=node.certainty.value,
                    temporality=node.temporality.value,
                    split_basis="evidence_event_frame",
                    required=True,
                    assertion_cue_text=(
                        assertion.assertion_cue_text if assertion is not None else None
                    ),
                    assertion_scope_text=(
                        assertion.assertion_scope_text if assertion is not None else None
                    ),
                    clinical_object_type=node.node_type.value,
                    clinical_object_assertion_id=(
                        assertion.object_id if assertion is not None else None
                    ),
                    source_frame_node_ids=[node.frame_node_id],
                    context_frame_node_ids=[
                        context_node.frame_node_id for context_node in context_nodes
                    ],
                    parent_frame_node_id=node.parent_node_id,
                    relation_to_parent=(
                        node.relation_to_parent.value
                        if node.relation_to_parent is not None
                        else None
                    ),
                    inherited_context_text=inherited_context_text,
                    local_content_text=node.node_text,
                    atomization_policy=node.atomization_policy.value,
                )
            )
            unit_index += 1

        return units


def _context_nodes(
    node: EvidenceFrameNode,
    nodes_by_id: dict[str, EvidenceFrameNode],
) -> list[EvidenceFrameNode]:
    context_ids: list[str] = []
    ancestor_ids = _ancestor_ids(node, nodes_by_id)
    explicit_ids = node.inherited_context_node_ids

    for node_id in [*ancestor_ids, *explicit_ids]:
        context_node = nodes_by_id.get(node_id)
        if context_node is None:
            continue
        if context_node.frame_node_id == node.frame_node_id:
            continue
        if node_id in context_ids:
            continue
        if context_node.context_role in {
            ContextRole.INHERITED_CONTEXT,
            ContextRole.MODIFIER_CONTEXT,
            ContextRole.LOCAL_CONTENT,
        } or context_node.node_type in {
            FrameNodeType.TEMPORAL_CONTEXT,
            FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT,
            FrameNodeType.MAIN_EVENT,
            FrameNodeType.CLINICAL_OBJECT,
            FrameNodeType.TREATMENT_EVENT,
        }:
            context_ids.append(node_id)

    return [nodes_by_id[node_id] for node_id in context_ids]


def _ancestor_ids(
    node: EvidenceFrameNode,
    nodes_by_id: dict[str, EvidenceFrameNode],
) -> list[str]:
    result: list[str] = []
    current = node
    seen: set[str] = set()
    while current.parent_node_id is not None:
        parent_id = current.parent_node_id
        if parent_id in seen:
            break
        seen.add(parent_id)
        parent = nodes_by_id.get(parent_id)
        if parent is None:
            break
        result.append(parent.frame_node_id)
        current = parent
    result.reverse()
    return result


def _compose_text(nodes: list[EvidenceFrameNode]) -> str | None:
    parts = _dedupe([node.node_text for node in nodes if node.node_text])
    if not parts:
        return None
    return "".join(parts)


def _compose_surface_text(
    inherited_context_text: str | None,
    local_text: str,
) -> str:
    if inherited_context_text is None:
        return local_text.strip()
    if local_text in inherited_context_text:
        return inherited_context_text.strip()
    separator = "，" if _looks_cjk(inherited_context_text + local_text) else ", "
    return f"{inherited_context_text}{separator}{local_text}".strip()


def _clinical_object_text(
    node: EvidenceFrameNode,
    nodes_by_id: dict[str, EvidenceFrameNode],
) -> str:
    if node.node_type != FrameNodeType.OBJECT_PROPERTY:
        return node.node_text
    parent = nodes_by_id.get(node.parent_node_id or "")
    if parent is None:
        return node.node_text
    return parent.node_text


def _matching_assertion(
    node: EvidenceFrameNode,
    assertions: list[ClinicalObjectAssertion],
) -> ClinicalObjectAssertion | None:
    for assertion in assertions:
        if assertion.object_text == node.node_text:
            return assertion
    for assertion in assertions:
        if assertion.object_text in node.node_text or node.node_text in assertion.object_text:
            return assertion
    return None


def _looks_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _span_ids(candidate: AtomizationCandidate) -> list[str]:
    return [
        span_id
        for span in candidate.source_spans
        if isinstance((span_id := span.get("span_id")), str) and span_id.strip()
    ]


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        if not cleaned or cleaned in result:
            continue
        result.append(cleaned)
    return result


def _warning(
    *,
    code: str,
    message: str,
    related_item_id: str | None = None,
    severity: ValidationSeverity = ValidationSeverity.WARNING,
) -> AtomizationWarning:
    return AtomizationWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
    )
