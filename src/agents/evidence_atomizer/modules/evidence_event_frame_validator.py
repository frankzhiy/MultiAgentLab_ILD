from __future__ import annotations

from collections import defaultdict, deque
from enum import StrEnum
from typing import Any

from pydantic import ValidationError

from src.schemas.evidence_atomizer import AtomizationWarning
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalObjectAssertion,
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_atomizer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
    ValidationSeverity,
)
from src.schemas.evidence_atomizer.evidence_event_frame import (
    AtomizationPolicy,
    ContextRole,
    EvidenceEventFrame,
    EvidenceFrameNode,
    FrameNodeType,
    FrameRelationType,
)
from src.utils.id_generator import (
    generate_evidence_frame_id,
    generate_evidence_frame_node_id,
)

from .atomization_candidate_builder import AtomizationCandidate


class EvidenceEventFrameValidator:
    """Validate assertion-grounded EvidenceEventFrame constraints."""

    _CONTEXT_ONLY_TYPES = {
        FrameNodeType.TEMPORAL_CONTEXT,
        FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT,
    }
    _PROPERTY_PARENT_TYPES = {
        FrameNodeType.CLINICAL_OBJECT,
        FrameNodeType.TEST_OR_MEASUREMENT,
        FrameNodeType.MAIN_EVENT,
        FrameNodeType.TREATMENT_EVENT,
        FrameNodeType.UNCERTAIN_OR_OTHER,
    }
    _FINDING_EQUIVALENT_TYPES = {
        FrameNodeType.OBJECT_PROPERTY,
        FrameNodeType.CLINICAL_OBJECT,
        FrameNodeType.TEST_OR_MEASUREMENT,
        FrameNodeType.UNCERTAIN_OR_OTHER,
    }

    def validate(
        self,
        *,
        candidate: AtomizationCandidate,
        assertions: list[ClinicalObjectAssertion],
        draft_payload: dict[str, Any],
    ) -> tuple[EvidenceEventFrame | None, list[AtomizationWarning]]:
        warnings: list[AtomizationWarning] = []
        source_text = candidate.source_text.strip()
        if not source_text:
            return None, [
                _warning(
                    code="frame_missing_source_text",
                    message=(
                        "EvidenceEventFrame could not be built because candidate.source_text was empty."
                    ),
                    related_item_id=candidate.item_id,
                )
            ]

        raw_nodes = draft_payload.get("frame_nodes")
        if not isinstance(raw_nodes, list):
            return None, [
                _warning(
                    code="frame_missing_nodes",
                    message="EvidenceEventFrame draft did not contain a frame_nodes array.",
                    related_item_id=candidate.item_id,
                    severity=ValidationSeverity.ERROR,
                )
            ]

        warnings.extend(
            _normalize_frame_warnings(
                candidate.item_id,
                draft_payload.get("frame_warnings"),
            )
        )

        assertions_by_id = {
            assertion.object_id: assertion
            for assertion in assertions
        }
        valid_assertion_ids = set(assertions_by_id)
        valid_span_ids = _span_ids(candidate)
        valid_attribute_ids = {
            attribute.attribute_id for attribute in candidate.attributes
        }
        deferred_assertion_ids = _normalize_deferred_assertion_ids(
            item_id=candidate.item_id,
            assertions_by_id=assertions_by_id,
            raw_deferred_ids=draft_payload.get("deferred_assertion_ids"),
            warnings=warnings,
        )

        raw_id_to_final_id: dict[str, str] = {}
        normalized_by_raw_id: dict[str, EvidenceFrameNode] = {}
        children_by_raw_parent_id: dict[str, list[str]] = defaultdict(list)
        discarded_raw_ids: set[str] = set()

        for index, raw_node in enumerate(raw_nodes, start=1):
            if not isinstance(raw_node, dict):
                warnings.append(
                    _warning(
                        code="frame_invalid_node",
                        message="EvidenceEventFrame draft contained a non-object node.",
                        related_item_id=candidate.item_id,
                    )
                )
                continue
            raw_id = _raw_node_id(raw_node, index)
            raw_id_to_final_id[raw_id] = generate_evidence_frame_node_id()

        for index, raw_node in enumerate(raw_nodes, start=1):
            if not isinstance(raw_node, dict):
                continue
            raw_id = _raw_node_id(raw_node, index)
            parent_raw_id = _text(raw_node.get("parent_node_id"))
            if parent_raw_id is not None:
                children_by_raw_parent_id[parent_raw_id].append(raw_id)

        for index, raw_node in enumerate(raw_nodes, start=1):
            if not isinstance(raw_node, dict):
                continue

            raw_id = _raw_node_id(raw_node, index)
            node_text = _text(raw_node.get("node_text"))
            if node_text is None or node_text not in source_text:
                discarded_raw_ids.add(raw_id)
                warnings.append(
                    _warning(
                        code="frame_node_text_not_in_source",
                        message=(
                            "Frame node text was not a continuous substring of candidate.source_text and was discarded."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )
                continue

            requested_span_ids = _list_text(raw_node.get("source_span_ids"))
            source_span_ids = [
                span_id for span_id in requested_span_ids if span_id in valid_span_ids
            ]
            invalid_span_ids = [
                span_id for span_id in requested_span_ids if span_id not in valid_span_ids
            ]
            if invalid_span_ids:
                warnings.append(
                    _warning(
                        code="frame_invalid_span_reference",
                        message=(
                            "Frame node referenced source_span_ids outside the candidate and those references were removed."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )
            if not source_span_ids:
                source_span_ids = valid_span_ids

            requested_attribute_ids = _list_text(raw_node.get("source_attribute_ids"))
            source_attribute_ids = [
                attribute_id
                for attribute_id in requested_attribute_ids
                if attribute_id in valid_attribute_ids
            ]
            invalid_attribute_ids = [
                attribute_id
                for attribute_id in requested_attribute_ids
                if attribute_id not in valid_attribute_ids
            ]
            if invalid_attribute_ids:
                warnings.append(
                    _warning(
                        code="frame_invalid_attribute_reference",
                        message=(
                            "Frame node referenced source_attribute_ids outside the candidate and those references were removed."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )

            requested_assertion_ids = _list_text(raw_node.get("source_assertion_ids"))
            source_assertion_ids = [
                assertion_id
                for assertion_id in requested_assertion_ids
                if assertion_id in valid_assertion_ids
            ]
            invalid_assertion_ids = [
                assertion_id
                for assertion_id in requested_assertion_ids
                if assertion_id not in valid_assertion_ids
            ]
            if invalid_assertion_ids:
                warnings.append(
                    _warning(
                        code="frame_invalid_assertion_reference",
                        message=(
                            "Frame node referenced ClinicalObjectAssertion ids outside the candidate and those references were removed."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )

            node_type = _coerce_enum(
                raw_node.get("node_type"),
                FrameNodeType,
                FrameNodeType.UNCERTAIN_OR_OTHER,
            )
            policy = _coerce_enum(
                raw_node.get("atomization_policy"),
                AtomizationPolicy,
                AtomizationPolicy.DEFER,
            )
            atomizable = bool(raw_node.get("atomizable"))
            if atomizable and policy in {
                AtomizationPolicy.DO_NOT_GENERATE_CONTEXT_ONLY,
                AtomizationPolicy.DEFER,
            }:
                atomizable = False
                warnings.append(
                    _warning(
                        code="frame_atomization_policy_corrected",
                        message=(
                            "Frame node atomizable flag conflicted with a non-generating atomization_policy and was corrected to false."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )
            if node_type in self._CONTEXT_ONLY_TYPES:
                atomizable = False

            parent_raw_id = _text(raw_node.get("parent_node_id"))
            parent_node_id = (
                raw_id_to_final_id.get(parent_raw_id)
                if parent_raw_id is not None
                else None
            )
            if parent_raw_id is not None and parent_node_id is None:
                warnings.append(
                    _warning(
                        code="frame_parent_missing",
                        message=(
                            "Frame node parent_node_id did not reference a draft node and the node was discarded."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )
                discarded_raw_ids.add(raw_id)
                continue

            relation = _coerce_optional_enum(
                raw_node.get("relation_to_parent"),
                FrameRelationType,
            )
            if parent_node_id is not None and relation is None:
                relation = FrameRelationType.OTHER_RELATION
                warnings.append(
                    _warning(
                        code="frame_relation_defaulted",
                        message=(
                            "A non-root frame node was missing relation_to_parent and was defaulted to other_relation."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )

            inherited_context_node_ids = [
                raw_id_to_final_id[context_raw_id]
                for context_raw_id in _list_text(raw_node.get("inherited_context_node_ids"))
                if context_raw_id in raw_id_to_final_id
            ]
            missing_context_refs = [
                context_raw_id
                for context_raw_id in _list_text(raw_node.get("inherited_context_node_ids"))
                if context_raw_id not in raw_id_to_final_id
            ]
            if missing_context_refs:
                warnings.append(
                    _warning(
                        code="frame_invalid_context_reference",
                        message=(
                            "Frame node inherited_context_node_ids included unknown node ids and those references were removed."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )

            try:
                normalized_by_raw_id[raw_id] = EvidenceFrameNode(
                    frame_node_id=raw_id_to_final_id[raw_id],
                    source_item_id=candidate.item_id,
                    node_type=node_type,
                    node_text=node_text,
                    assertion_status=_coerce_enum(
                        raw_node.get("assertion_status"),
                        NegationStatus,
                        _coerce_enum(
                            candidate.negation,
                            NegationStatus,
                            NegationStatus.UNKNOWN,
                        ),
                    ),
                    certainty=_coerce_enum(
                        raw_node.get("certainty"),
                        CertaintyLevel,
                        _coerce_enum(
                            candidate.certainty,
                            CertaintyLevel,
                            CertaintyLevel.UNKNOWN,
                        ),
                    ),
                    temporality=_coerce_enum(
                        raw_node.get("temporality"),
                        TemporalRelation,
                        _coerce_enum(
                            candidate.temporality,
                            TemporalRelation,
                            TemporalRelation.UNKNOWN,
                        ),
                    ),
                    parent_node_id=parent_node_id,
                    relation_to_parent=relation,
                    inherited_context_node_ids=inherited_context_node_ids,
                    source_assertion_ids=source_assertion_ids,
                    source_attribute_ids=source_attribute_ids,
                    source_span_ids=source_span_ids,
                    context_role=_coerce_enum(
                        raw_node.get("context_role"),
                        ContextRole,
                        ContextRole.UNCERTAIN,
                    ),
                    atomizable=atomizable,
                    atomization_policy=policy,
                    confidence=_coerce_enum(
                        raw_node.get("confidence"),
                        ConfidenceLevel,
                        ConfidenceLevel.MEDIUM,
                    ),
                    notes=_text(raw_node.get("notes")),
                )
            except (TypeError, ValueError, ValidationError):
                discarded_raw_ids.add(raw_id)
                warnings.append(
                    _warning(
                        code="frame_invalid_node",
                        message="Frame node failed schema validation and was discarded.",
                        related_item_id=candidate.item_id,
                    )
                )

        discarded_raw_ids.update(_descendants(discarded_raw_ids, children_by_raw_parent_id))
        kept_nodes = [
            node
            for raw_id, node in normalized_by_raw_id.items()
            if raw_id not in discarded_raw_ids
            and (
                node.parent_node_id is None
                or _parent_kept(node.parent_node_id, normalized_by_raw_id, discarded_raw_ids)
            )
        ]
        kept_node_ids = {node.frame_node_id for node in kept_nodes}
        kept_nodes = [
            node.model_copy(
                update={
                    "inherited_context_node_ids": [
                        context_id
                        for context_id in node.inherited_context_node_ids
                        if context_id in kept_node_ids
                    ]
                }
            )
            for node in kept_nodes
        ]

        if _has_cycle(kept_nodes):
            warnings.append(
                _warning(
                    code="frame_cycle_detected",
                    message="EvidenceEventFrame parent references contain a cycle.",
                    related_item_id=candidate.item_id,
                    severity=ValidationSeverity.ERROR,
                )
            )
            return None, warnings

        if kept_nodes:
            relation_warnings = _relation_warnings(
                candidate=candidate,
                assertions=assertions,
                nodes=kept_nodes,
            )
            warnings.extend(relation_warnings)
            if _has_error_warning(relation_warnings):
                return None, warnings

            corrected_nodes = _correct_root_whole_source_atomizable(
                candidate=candidate,
                assertions=assertions,
                nodes=kept_nodes,
                warnings=warnings,
            )
            if corrected_nodes is None:
                return None, warnings
            kept_nodes = corrected_nodes

        deferred_assertion_ids = _prune_mapped_deferred_assertion_ids(
            item_id=candidate.item_id,
            nodes=kept_nodes,
            deferred_assertion_ids=deferred_assertion_ids,
            warnings=warnings,
        )

        coverage_warnings = _assertion_coverage_warnings(
            candidate=candidate,
            assertions_by_id=assertions_by_id,
            nodes=kept_nodes,
            deferred_assertion_ids=deferred_assertion_ids,
        )
        warnings.extend(coverage_warnings)
        if _has_error_warning(coverage_warnings):
            return None, warnings

        if kept_nodes:
            degeneracy_warnings = _degenerate_frame_warnings(
                candidate=candidate,
                assertions=assertions,
                nodes=kept_nodes,
            )
            warnings.extend(degeneracy_warnings)
            if _has_error_warning(degeneracy_warnings):
                return None, warnings

        if kept_nodes and not any(node.atomizable for node in kept_nodes):
            warnings.append(
                _warning(
                    code="frame_no_atomizable_node",
                    message=(
                        "EvidenceEventFrame contains no atomizable nodes after validation and will not generate coverage units."
                    ),
                    related_item_id=candidate.item_id,
                )
            )

        if not kept_nodes and not deferred_assertion_ids and not valid_assertion_ids:
            warnings.append(
                _warning(
                    code="frame_empty_after_validation",
                    message="EvidenceEventFrame contained no usable nodes after validation.",
                    related_item_id=candidate.item_id,
                    severity=ValidationSeverity.ERROR,
                )
            )
            return None, warnings

        try:
            frame = EvidenceEventFrame(
                frame_id=generate_evidence_frame_id(),
                source_item_id=candidate.item_id,
                source_text=source_text,
                frame_nodes=kept_nodes,
                deferred_assertion_ids=deferred_assertion_ids,
                frame_warnings=warnings,
            )
        except (TypeError, ValueError, ValidationError) as exc:
            warnings.append(
                _warning(
                    code="frame_invalid",
                    message=(
                        f"EvidenceEventFrame failed schema validation: {type(exc).__name__}."
                    ),
                    related_item_id=candidate.item_id,
                )
            )
            return None, warnings

        return frame, warnings


def _has_cycle(nodes: list[EvidenceFrameNode]) -> bool:
    parents = {
        node.frame_node_id: node.parent_node_id
        for node in nodes
        if node.parent_node_id is not None
    }
    for node_id in parents:
        seen: set[str] = set()
        current: str | None = node_id
        while current is not None:
            if current in seen:
                return True
            seen.add(current)
            current = parents.get(current)
    return False


def _relation_warnings(
    *,
    candidate: AtomizationCandidate,
    assertions: list[ClinicalObjectAssertion],
    nodes: list[EvidenceFrameNode],
) -> list[AtomizationWarning]:
    warnings: list[AtomizationWarning] = []
    nodes_by_id = {node.frame_node_id: node for node in nodes}
    is_complex_item = len(assertions) >= 3

    if len(nodes) > 1:
        for node in nodes:
            if node.parent_node_id is None:
                continue
            if node.relation_to_parent is None:
                warnings.append(
                    _warning(
                        code="frame_relation_incomplete",
                        message=(
                            "A non-root frame node was missing relation_to_parent after normalization."
                        ),
                        related_item_id=candidate.item_id,
                        severity=ValidationSeverity.ERROR,
                    )
                )

    for node in nodes:
        if node.parent_node_id is not None and node.parent_node_id not in nodes_by_id:
            warnings.append(
                _warning(
                    code="frame_parent_missing",
                    message="Frame node parent_node_id does not reference a kept node.",
                    related_item_id=candidate.item_id,
                    severity=ValidationSeverity.ERROR,
                )
            )
            continue

        parent = nodes_by_id.get(node.parent_node_id or "")
        if node.node_type == FrameNodeType.OBJECT_PROPERTY:
            if parent is None:
                warnings.append(
                    _warning(
                        code="frame_orphan_property",
                        message="Object property frame node is missing a parent relationship.",
                        related_item_id=candidate.item_id,
                        severity=(
                            ValidationSeverity.ERROR
                            if is_complex_item
                            else ValidationSeverity.WARNING
                        ),
                    )
                )
            elif parent.node_type not in EvidenceEventFrameValidator._PROPERTY_PARENT_TYPES:
                warnings.append(
                    _warning(
                        code="frame_property_parent_type_unexpected",
                        message=(
                            "Object property frame node parent type may not provide stable local context for atomization."
                        ),
                        related_item_id=candidate.item_id,
                    )
                )

        if node.node_type == FrameNodeType.SYMPTOM_MODIFIER and parent is None:
            warnings.append(
                _warning(
                    code="frame_orphan_modifier",
                    message="Symptom modifier frame node does not have a clear modifier target.",
                    related_item_id=candidate.item_id,
                )
            )

    return warnings


def _correct_root_whole_source_atomizable(
    *,
    candidate: AtomizationCandidate,
    assertions: list[ClinicalObjectAssertion],
    nodes: list[EvidenceFrameNode],
    warnings: list[AtomizationWarning],
) -> list[EvidenceFrameNode] | None:
    if len(assertions) < 3:
        return nodes

    whole_source_root_ids = {
        node.frame_node_id
        for node in nodes
        if node.parent_node_id is None
        and node.atomizable
        and _same_text(node.node_text, candidate.source_text)
    }
    if not whole_source_root_ids:
        return nodes

    has_other_atomizable_nodes = any(
        node.atomizable and node.frame_node_id not in whole_source_root_ids
        for node in nodes
    )
    if not has_other_atomizable_nodes:
        warnings.append(
            _warning(
                code="root_whole_source_atomization_for_complex_item",
                message=(
                    "A complex item contained an atomizable root node whose node_text matched the full source_text, with no other atomizable assertion-grounded child nodes."
                ),
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )
        return None

    corrected_nodes: list[EvidenceFrameNode] = []
    for node in nodes:
        if node.frame_node_id not in whole_source_root_ids:
            corrected_nodes.append(node)
            continue
        corrected_nodes.append(
            node.model_copy(
                update={
                    "atomizable": False,
                    "atomization_policy": AtomizationPolicy.DEFER,
                }
            )
        )
    warnings.append(
        _warning(
            code="root_whole_source_atomizable_corrected",
            message=(
                "A full-source root node was corrected to non-atomizable because other assertion-grounded nodes were available."
            ),
            related_item_id=candidate.item_id,
        )
    )
    return corrected_nodes


def _assertion_coverage_warnings(
    *,
    candidate: AtomizationCandidate,
    assertions_by_id: dict[str, ClinicalObjectAssertion],
    nodes: list[EvidenceFrameNode],
    deferred_assertion_ids: list[str],
) -> list[AtomizationWarning]:
    warnings: list[AtomizationWarning] = []
    mapped_assertion_ids = _mapped_assertion_ids(nodes)
    missing_assertion_ids = (
        set(assertions_by_id)
        - mapped_assertion_ids
        - set(deferred_assertion_ids)
    )
    if assertions_by_id and missing_assertion_ids:
        warnings.append(
            _warning(
                code="frame_assertion_coverage_missing",
                message=(
                    "EvidenceEventFrame failed to map all ClinicalObjectAssertions. "
                    f"mapped={len(mapped_assertion_ids)} total={len(assertions_by_id)} "
                    f"missing={sorted(missing_assertion_ids)}"
                ),
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )
    return warnings


def _degenerate_frame_warnings(
    *,
    candidate: AtomizationCandidate,
    assertions: list[ClinicalObjectAssertion],
    nodes: list[EvidenceFrameNode],
) -> list[AtomizationWarning]:
    warnings: list[AtomizationWarning] = []
    assertion_count = len(assertions)
    atomizable_nodes = [node for node in nodes if node.atomizable]
    nodes_by_id = {node.frame_node_id: node for node in nodes}

    if assertion_count >= 3 and len(nodes) <= 1:
        warnings.append(
            _warning(
                code="degenerate_frame_single_node",
                message="A multi-assertion item collapsed into a single frame node.",
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )

    if (
        assertion_count >= 3
        and len(atomizable_nodes) == 1
        and _same_text(atomizable_nodes[0].node_text, candidate.source_text)
    ):
        warnings.append(
            _warning(
                code="degenerate_frame_full_source_atomizable",
                message=(
                    "A multi-assertion item collapsed into one atomizable full-source frame node."
                ),
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )

    mapped_node_ids_by_assertion: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        for assertion_id in node.source_assertion_ids:
            mapped_node_ids_by_assertion[assertion_id].add(node.frame_node_id)
    unique_mapped_node_ids = {
        node_id
        for node_ids in mapped_node_ids_by_assertion.values()
        for node_id in node_ids
    }
    if assertion_count >= 3 and len(unique_mapped_node_ids) == 1:
        node = nodes_by_id[next(iter(unique_mapped_node_ids))]
        if (
            node.node_type == FrameNodeType.MAIN_EVENT
            and _same_text(node.node_text, candidate.source_text)
        ):
            warnings.append(
                _warning(
                    code="degenerate_frame_assertions_collapsed",
                    message=(
                        "All mapped clinical assertions collapsed into the same full-source main_event node."
                    ),
                    related_item_id=candidate.item_id,
                    severity=ValidationSeverity.ERROR,
                )
            )

    absent_assertion_ids = {
        assertion.object_id
        for assertion in assertions
        if assertion.assertion_status == ClinicalObjectAssertionStatus.ABSENT
        and assertion.object_type in {
            ClinicalObjectType.SYMPTOM,
            ClinicalObjectType.SIGN,
            ClinicalObjectType.FINDING,
        }
    }
    if absent_assertion_ids and not any(
        node.node_type == FrameNodeType.NEGATIVE_FINDING
        and bool(set(node.source_assertion_ids) & absent_assertion_ids)
        for node in nodes
    ):
        warnings.append(
            _warning(
                code="frame_missing_negative_finding_structure",
                message=(
                    "Absent symptom or finding assertions were present, but the frame did not include a mapped negative_finding node."
                ),
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )

    finding_assertion_ids = {
        assertion.object_id
        for assertion in assertions
        if assertion.object_type in {
            ClinicalObjectType.FINDING,
            ClinicalObjectType.IMAGING_FINDING,
        }
    }
    if finding_assertion_ids and not any(
        node.node_type in EvidenceEventFrameValidator._FINDING_EQUIVALENT_TYPES
        and bool(set(node.source_assertion_ids) & finding_assertion_ids)
        for node in nodes
    ):
        warnings.append(
            _warning(
                code="frame_missing_finding_structure",
                message=(
                    "Finding assertions were present, but the frame did not include mapped object_property, clinical_object, or equivalent structural nodes."
                ),
                related_item_id=candidate.item_id,
            )
        )

    management_assertion_ids = {
        assertion.object_id
        for assertion in assertions
        if assertion.object_type == ClinicalObjectType.CARE_SEEKING_OR_MANAGEMENT
    }
    if management_assertion_ids and not any(
        node.node_type == FrameNodeType.MANAGEMENT_EVENT
        and bool(set(node.source_assertion_ids) & management_assertion_ids)
        for node in nodes
    ):
        warnings.append(
            _warning(
                code="frame_missing_management_structure",
                message=(
                    "Management assertions were present, but the frame did not include mapped management_event nodes."
                ),
                related_item_id=candidate.item_id,
            )
        )

    treatment_assertion_ids = {
        assertion.object_id
        for assertion in assertions
        if assertion.object_type in {
            ClinicalObjectType.TREATMENT,
            ClinicalObjectType.MEDICATION,
            ClinicalObjectType.PROCEDURE,
        }
    }
    if treatment_assertion_ids and not any(
        node.node_type == FrameNodeType.TREATMENT_EVENT
        and bool(set(node.source_assertion_ids) & treatment_assertion_ids)
        for node in nodes
    ):
        warnings.append(
            _warning(
                code="frame_missing_treatment_structure",
                message=(
                    "Treatment assertions were present, but the frame did not include mapped treatment_event nodes."
                ),
                related_item_id=candidate.item_id,
            )
        )

    response_assertion_ids = {
        assertion.object_id
        for assertion in assertions
        if assertion.object_type == ClinicalObjectType.TREATMENT_RESPONSE
    }
    if response_assertion_ids and not any(
        node.node_type == FrameNodeType.TREATMENT_RESPONSE
        and bool(set(node.source_assertion_ids) & response_assertion_ids)
        for node in nodes
    ):
        warnings.append(
            _warning(
                code="frame_missing_treatment_response_structure",
                message=(
                    "Treatment response assertions were present, but the frame did not include mapped treatment_response nodes."
                ),
                related_item_id=candidate.item_id,
            )
        )

    return warnings


def _descendants(
    root_ids: set[str],
    children_by_parent: dict[str, list[str]],
) -> set[str]:
    result: set[str] = set()
    queue = deque(root_ids)
    while queue:
        raw_id = queue.popleft()
        for child_id in children_by_parent.get(raw_id, []):
            if child_id in result:
                continue
            result.add(child_id)
            queue.append(child_id)
    return result


def _raw_node_id(raw_node: dict[str, Any], index: int) -> str:
    return _text(raw_node.get("frame_node_id")) or f"tmp_node_{index:03d}"


def _parent_kept(
    parent_node_id: str,
    normalized_by_raw_id: dict[str, EvidenceFrameNode],
    discarded_raw_ids: set[str],
) -> bool:
    for raw_id, node in normalized_by_raw_id.items():
        if node.frame_node_id == parent_node_id:
            return raw_id not in discarded_raw_ids
    return False


def _span_ids(candidate: AtomizationCandidate) -> list[str]:
    return [
        span_id
        for span in candidate.source_spans
        if (span_id := _text(span.get("span_id"))) is not None
    ]


def _mapped_assertion_ids(nodes: list[EvidenceFrameNode]) -> set[str]:
    return {
        assertion_id
        for node in nodes
        for assertion_id in node.source_assertion_ids
    }


def _prune_mapped_deferred_assertion_ids(
    *,
    item_id: str,
    nodes: list[EvidenceFrameNode],
    deferred_assertion_ids: list[str],
    warnings: list[AtomizationWarning],
) -> list[str]:
    mapped_assertion_ids = _mapped_assertion_ids(nodes)
    overlap = mapped_assertion_ids & set(deferred_assertion_ids)
    if not overlap:
        return deferred_assertion_ids

    warnings.append(
        _warning(
            code="deferred_assertion_already_mapped",
            message=(
                "Some deferred_assertion_ids were already covered by frame nodes and were removed from deferred_assertion_ids. "
                f"overlap={sorted(overlap)}"
            ),
            related_item_id=item_id,
        )
    )
    return [
        assertion_id
        for assertion_id in deferred_assertion_ids
        if assertion_id not in overlap
    ]


def _normalize_deferred_assertion_ids(
    *,
    item_id: str,
    assertions_by_id: dict[str, ClinicalObjectAssertion],
    raw_deferred_ids: Any,
    warnings: list[AtomizationWarning],
) -> list[str]:
    deferred_assertion_ids: list[str] = []
    invalid_assertion_ids: list[str] = []
    for assertion_id in _list_text(raw_deferred_ids):
        if assertion_id in assertions_by_id:
            if assertion_id not in deferred_assertion_ids:
                deferred_assertion_ids.append(assertion_id)
            continue
        invalid_assertion_ids.append(assertion_id)

    if invalid_assertion_ids:
        warnings.append(
            _warning(
                code="frame_invalid_assertion_reference",
                message=(
                    "deferred_assertion_ids referenced ClinicalObjectAssertion ids outside the candidate and those references were removed."
                ),
                related_item_id=item_id,
            )
        )

    if deferred_assertion_ids:
        generic_defer_warnings = [
            warning
            for warning in warnings
            if "defer" in warning.code.lower() or "defer" in warning.message.lower()
        ]
        for assertion_id in deferred_assertion_ids:
            assertion = assertions_by_id.get(assertion_id)
            if assertion is None:
                continue
            if _has_deferred_reason(assertion_id, assertion, generic_defer_warnings, deferred_assertion_ids):
                continue
            warnings.append(
                _warning(
                    code="deferred_assertion_without_reason",
                    message=(
                        "A deferred assertion did not have a corresponding frame warning explaining the deferral. "
                        f"assertion_id={assertion_id}"
                    ),
                    related_item_id=item_id,
                )
            )

    return deferred_assertion_ids


def _has_deferred_reason(
    assertion_id: str,
    assertion: ClinicalObjectAssertion,
    warnings: list[AtomizationWarning],
    deferred_assertion_ids: list[str],
) -> bool:
    if not warnings:
        return False
    if len(deferred_assertion_ids) == 1:
        return True
    for warning in warnings:
        warning_text = f"{warning.code} {warning.message}".lower()
        if assertion_id.lower() in warning_text:
            return True
        if assertion.object_text.lower() in warning_text:
            return True
    return False


def _same_text(left: str, right: str) -> bool:
    return " ".join(left.split()) == " ".join(right.split())


def _has_error_warning(warnings: list[AtomizationWarning]) -> bool:
    return any(warning.severity == ValidationSeverity.ERROR for warning in warnings)


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, StrEnum):
        value = value.value
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return None


def _list_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_list_text(item))
        return result
    return []


def _coerce_enum(value: Any, enum_type: type[StrEnum], default: StrEnum) -> StrEnum:
    allowed = {item.value: item for item in enum_type}
    if isinstance(value, enum_type):
        return value
    if isinstance(value, StrEnum):
        value = value.value
    if isinstance(value, str) and value in allowed:
        return allowed[value]
    return default


def _coerce_optional_enum(
    value: Any,
    enum_type: type[StrEnum],
) -> StrEnum | None:
    allowed = {item.value: item for item in enum_type}
    if isinstance(value, enum_type):
        return value
    if isinstance(value, StrEnum):
        value = value.value
    if isinstance(value, str) and value in allowed:
        return allowed[value]
    return None


def _normalize_frame_warnings(
    item_id: str,
    raw_warnings: Any,
) -> list[AtomizationWarning]:
    if not isinstance(raw_warnings, list):
        return []
    warnings: list[AtomizationWarning] = []
    for raw_warning in raw_warnings:
        if not isinstance(raw_warning, dict):
            continue
        code = _text(raw_warning.get("code")) or "frame_builder_warning"
        message = _text(raw_warning.get("message")) or "Frame builder reported a warning."
        severity = _coerce_enum(
            raw_warning.get("severity"),
            ValidationSeverity,
            ValidationSeverity.WARNING,
        )
        warnings.append(
            _warning(
                code=code,
                message=message,
                related_item_id=_text(raw_warning.get("related_item_id")) or item_id,
                severity=severity,
            )
        )
    return warnings


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
