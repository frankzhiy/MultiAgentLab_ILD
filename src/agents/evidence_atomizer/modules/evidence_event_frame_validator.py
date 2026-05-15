from __future__ import annotations

from collections import defaultdict, deque
from enum import StrEnum
from typing import Any

from pydantic import ValidationError

from src.schemas.evidence_atomizer import AtomizationWarning
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
    """Validate executable EvidenceEventFrame constraints without redoing semantics."""

    _CONTEXT_ONLY_TYPES = {
        FrameNodeType.TEMPORAL_CONTEXT,
        FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT,
    }

    def validate(
        self,
        *,
        candidate: AtomizationCandidate,
        draft_payload: dict[str, Any],
    ) -> tuple[EvidenceEventFrame | None, list[AtomizationWarning]]:
        warnings: list[AtomizationWarning] = []
        source_text = candidate.source_text.strip()
        if not source_text:
            return None, [
                _warning(
                    code="frame_missing_source_text",
                    message="EvidenceEventFrame could not be built because candidate.source_text was empty.",
                    related_item_id=candidate.item_id,
                )
            ]

        raw_nodes = draft_payload.get("frame_nodes")
        if not isinstance(raw_nodes, list):
            return None, [
                _warning(
                    code="frame_no_atomizable_node",
                    message="EvidenceEventFrame draft did not contain frame_nodes.",
                    related_item_id=candidate.item_id,
                )
            ]
        warnings.extend(
            _normalize_frame_warnings(
                candidate.item_id,
                draft_payload.get("frame_warnings"),
            )
        )

        valid_span_ids = _span_ids(candidate)
        valid_attribute_ids = {attribute.attribute_id for attribute in candidate.attributes}
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

            raw_id = _text(raw_node.get("frame_node_id")) or f"tmp_node_{index:03d}"
            raw_id_to_final_id[raw_id] = generate_evidence_frame_node_id()

        for raw_node in raw_nodes:
            if not isinstance(raw_node, dict):
                continue
            raw_id = _text(raw_node.get("frame_node_id"))
            if raw_id is None:
                continue
            parent_raw_id = _text(raw_node.get("parent_node_id"))
            if parent_raw_id is not None:
                children_by_raw_parent_id[parent_raw_id].append(raw_id)

        for raw_node in raw_nodes:
            if not isinstance(raw_node, dict):
                continue
            raw_id = _text(raw_node.get("frame_node_id"))
            if raw_id is None:
                continue

            node_text = _text(raw_node.get("node_text"))
            if node_text is None or node_text not in source_text:
                discarded_raw_ids.add(raw_id)
                warnings.append(
                    _warning(
                        code="frame_node_text_not_in_source",
                        message="Frame node text was not a continuous substring of candidate.source_text and was discarded.",
                        related_item_id=candidate.item_id,
                    )
                )
                continue

            source_span_ids = [
                span_id
                for span_id in _list_text(raw_node.get("source_span_ids"))
                if span_id in valid_span_ids
            ]
            invalid_span_ids = [
                span_id
                for span_id in _list_text(raw_node.get("source_span_ids"))
                if span_id not in valid_span_ids
            ]
            if invalid_span_ids:
                warnings.append(
                    _warning(
                        code="frame_invalid_span_reference",
                        message="Frame node referenced source_span_ids outside the candidate and those references were removed.",
                        related_item_id=candidate.item_id,
                    )
                )
            if not source_span_ids:
                source_span_ids = valid_span_ids

            source_attribute_ids = [
                attribute_id
                for attribute_id in _list_text(raw_node.get("source_attribute_ids"))
                if attribute_id in valid_attribute_ids
            ]
            invalid_attribute_ids = [
                attribute_id
                for attribute_id in _list_text(raw_node.get("source_attribute_ids"))
                if attribute_id not in valid_attribute_ids
            ]
            if invalid_attribute_ids:
                warnings.append(
                    _warning(
                        code="frame_invalid_attribute_reference",
                        message="Frame node referenced source_attribute_ids outside the candidate and those references were removed.",
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
            if node_type in self._CONTEXT_ONLY_TYPES and policy == AtomizationPolicy.DO_NOT_GENERATE_CONTEXT_ONLY:
                atomizable = False
            if atomizable and policy == AtomizationPolicy.DO_NOT_GENERATE_CONTEXT_ONLY:
                atomizable = False
                warnings.append(
                    _warning(
                        code="frame_no_atomizable_node",
                        message="Context-only frame node was marked atomizable and was corrected to non-atomizable.",
                        related_item_id=candidate.item_id,
                    )
                )

            parent_raw_id = _text(raw_node.get("parent_node_id"))
            relation = _coerce_optional_enum(
                raw_node.get("relation_to_parent"),
                FrameRelationType,
            )
            parent_node_id = (
                raw_id_to_final_id.get(parent_raw_id)
                if parent_raw_id is not None
                else None
            )
            if parent_raw_id is not None and parent_node_id is None:
                warnings.append(
                    _warning(
                        code="frame_parent_missing",
                        message="Frame node parent_node_id did not reference a draft node and the node was discarded.",
                        related_item_id=candidate.item_id,
                    )
                )
                discarded_raw_ids.add(raw_id)
                continue
            if parent_node_id is not None and relation is None:
                relation = FrameRelationType.OTHER_RELATION

            inherited_context_node_ids = [
                raw_id_to_final_id[context_raw_id]
                for context_raw_id in _list_text(
                    raw_node.get("inherited_context_node_ids")
                )
                if context_raw_id in raw_id_to_final_id
            ]
            missing_context_refs = [
                context_raw_id
                for context_raw_id in _list_text(
                    raw_node.get("inherited_context_node_ids")
                )
                if context_raw_id not in raw_id_to_final_id
            ]
            if missing_context_refs:
                warnings.append(
                    _warning(
                        code="frame_invalid_context_reference",
                        message="Frame node inherited_context_node_ids included unknown node ids and those references were removed.",
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

        discarded_raw_ids.update(
            _descendants(discarded_raw_ids, children_by_raw_parent_id)
        )
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

        structural_warnings = _structural_warnings(candidate, kept_nodes)
        warnings.extend(structural_warnings)
        if any(warning.code == "frame_cycle_detected" for warning in structural_warnings):
            return None, warnings
        if not kept_nodes or not any(node.atomizable for node in kept_nodes):
            warnings.append(
                _warning(
                    code="frame_no_atomizable_node",
                    message="EvidenceEventFrame has no atomizable node after validation.",
                    related_item_id=candidate.item_id,
                )
            )
            return None, warnings

        try:
            frame = EvidenceEventFrame(
                frame_id=generate_evidence_frame_id(),
                source_item_id=candidate.item_id,
                source_text=source_text,
                frame_nodes=kept_nodes,
                frame_warnings=warnings,
            )
        except (TypeError, ValueError, ValidationError) as exc:
            warnings.append(
                _warning(
                    code="frame_invalid",
                    message=f"EvidenceEventFrame failed schema validation: {type(exc).__name__}.",
                    related_item_id=candidate.item_id,
                )
            )
            return None, warnings

        return frame, warnings


def _structural_warnings(
    candidate: AtomizationCandidate,
    nodes: list[EvidenceFrameNode],
) -> list[AtomizationWarning]:
    warnings: list[AtomizationWarning] = []
    nodes_by_id = {node.frame_node_id: node for node in nodes}

    if _has_cycle(nodes):
        warnings.append(
            _warning(
                code="frame_cycle_detected",
                message="EvidenceEventFrame parent references contain a cycle.",
                related_item_id=candidate.item_id,
                severity=ValidationSeverity.ERROR,
            )
        )

    for node in nodes:
        if node.parent_node_id is None:
            continue
        parent = nodes_by_id.get(node.parent_node_id)
        if parent is None:
            warnings.append(
                _warning(
                    code="frame_parent_missing",
                    message="Frame node parent_node_id does not reference a kept node.",
                    related_item_id=candidate.item_id,
                )
            )
            continue
        if (
            node.node_type == FrameNodeType.OBJECT_PROPERTY
            and (
                node.relation_to_parent != FrameRelationType.PROPERTY_OF
                or parent.node_type != FrameNodeType.CLINICAL_OBJECT
            )
        ):
            warnings.append(
                _warning(
                    code="frame_orphan_property",
                    message="Object property frame node does not have a clear clinical-object parent.",
                    related_item_id=candidate.item_id,
                )
            )
        if (
            node.node_type == FrameNodeType.SYMPTOM_MODIFIER
            and node.relation_to_parent != FrameRelationType.MODIFIER_OF
        ):
            warnings.append(
                _warning(
                    code="frame_orphan_modifier",
                    message="Symptom modifier frame node does not have a clear modifier target.",
                    related_item_id=candidate.item_id,
                )
            )

    return warnings


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
