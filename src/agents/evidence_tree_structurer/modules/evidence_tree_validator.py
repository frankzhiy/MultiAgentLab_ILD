"""EvidenceTreeValidator.

Source-grounds and shape-checks the LLM-produced EvidenceTree payload for one
ItemContext. The validator is report-only: it drops invalid nodes with
warnings but never repairs structure beyond mapping raw_id -> final_id and
filtering invalid parent links / cycles.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.schemas.case_structurer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
)
from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalObjectAssertion,
)
from src.schemas.evidence_tree_structurer.common import ValidationSeverity
from src.schemas.evidence_tree_structurer.evidence_tree import (
    ALLOWED_PARENT_TYPES,
    LEAF_NODE_TYPES,
    ROOT_ALLOWED_NODE_TYPES,
    ContextRole,
    EvidenceTree,
    EvidenceTreeNode,
    EvidenceTreeNodeOrigin,
    EvidenceTreeNodeType,
    EvidenceTreeRelationType,
)
from src.schemas.evidence_tree_structurer.tree_structuring_warning import (
    TreeStructuringWarning,
)
from src.utils.id_generator import generate_evidence_tree_node_id

from .item_context import ItemContext


class EvidenceTreeValidator:
    """Validate one LLM payload into a typed EvidenceTree."""

    def validate(
        self,
        context: ItemContext,
        payload: dict[str, Any],
        assertions: list[ClinicalObjectAssertion],
    ) -> tuple[EvidenceTree | None, list[TreeStructuringWarning]]:
        warnings: list[TreeStructuringWarning] = []
        valid_assertion_ids = {assertion.object_id for assertion in assertions}
        valid_span_ids = set(context.span_ids)

        raw_nodes = payload.get("tree_nodes")
        if not isinstance(raw_nodes, list) or not raw_nodes:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "tree_payload_missing_nodes",
                    "LLM payload is missing a non-empty 'tree_nodes' list.",
                    related_item_id=context.item_id,
                )
            )
            return None, warnings

        # Pass 1: build raw_id -> final_id mapping; coerce per-node fields.
        coerced: dict[str, dict[str, Any]] = {}
        raw_to_final: dict[str, str] = {}
        for index, raw in enumerate(raw_nodes):
            if not isinstance(raw, dict):
                warnings.append(
                    _warning(
                        ValidationSeverity.WARNING,
                        "tree_node_dropped_invalid_shape",
                        f"Node #{index} dropped: expected a JSON object.",
                        related_item_id=context.item_id,
                    )
                )
                continue
            coerced_node, drop_reason = _coerce_node(
                raw,
                context=context,
                valid_assertion_ids=valid_assertion_ids,
                valid_span_ids=valid_span_ids,
            )
            if coerced_node is None:
                warnings.append(
                    _warning(
                        ValidationSeverity.WARNING,
                        "tree_node_dropped",
                        f"Node #{index} dropped: {drop_reason}",
                        related_item_id=context.item_id,
                    )
                )
                continue
            raw_id = str(raw.get("raw_id") or "").strip()
            if not raw_id or raw_id in raw_to_final:
                raw_id = f"raw_{index}"
            final_id = generate_evidence_tree_node_id()
            raw_to_final[raw_id] = final_id
            coerced_node["_raw_id"] = raw_id
            coerced_node["tree_node_id"] = final_id
            coerced[raw_id] = coerced_node

        if not coerced:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "tree_payload_all_nodes_dropped",
                    "All nodes were dropped during validation.",
                    related_item_id=context.item_id,
                )
            )
            return None, warnings

        # Pass 2: resolve parent links, detect cycles, check grammar.
        nodes_by_id: dict[str, dict[str, Any]] = {}
        for raw_id, node in coerced.items():
            parent_raw = node.pop("_parent_raw", None)
            if parent_raw is None:
                node["parent_node_id"] = None
                node["relation_to_parent"] = EvidenceTreeRelationType.ROOT_OF
            elif parent_raw not in raw_to_final:
                warnings.append(
                    _warning(
                        ValidationSeverity.WARNING,
                        "tree_node_parent_unresolved",
                        f"Node parent_raw_id '{parent_raw}' was not found; demoted to root.",
                        related_item_id=context.item_id,
                    )
                )
                node["parent_node_id"] = None
                node["relation_to_parent"] = EvidenceTreeRelationType.ROOT_OF
            else:
                node["parent_node_id"] = raw_to_final[parent_raw]
            # remap inherited_context
            remapped: list[str] = []
            for raw_ctx in node.pop("_inherited_raw", []):
                if raw_ctx in raw_to_final:
                    remapped.append(raw_to_final[raw_ctx])
            node["inherited_context_node_ids"] = remapped
            nodes_by_id[node["tree_node_id"]] = node

        # Cycle detection: simple DFS.
        cycle_nodes = _detect_cycle_node_ids(nodes_by_id)
        for cycle_id in cycle_nodes:
            warnings.append(
                _warning(
                    ValidationSeverity.WARNING,
                    "tree_node_cycle_detected",
                    "Cycle in parent_node_id chain; node demoted to root.",
                    related_item_id=context.item_id,
                    related_tree_node_id=cycle_id,
                )
            )
            nodes_by_id[cycle_id]["parent_node_id"] = None
            nodes_by_id[cycle_id]["relation_to_parent"] = EvidenceTreeRelationType.ROOT_OF

        # Grammar checks.
        for node in nodes_by_id.values():
            node_type = node["node_type"]
            parent_id = node["parent_node_id"]
            if parent_id is None:
                if node_type not in ROOT_ALLOWED_NODE_TYPES:
                    warnings.append(
                        _warning(
                            ValidationSeverity.WARNING,
                            "tree_grammar_root_not_allowed",
                            f"node_type '{node_type.value}' is not allowed as a tree root.",
                            related_item_id=context.item_id,
                            related_tree_node_id=node["tree_node_id"],
                        )
                    )
            else:
                allowed = ALLOWED_PARENT_TYPES.get(node_type)
                parent_type = nodes_by_id[parent_id]["node_type"]
                if allowed is not None and parent_type not in allowed:
                    warnings.append(
                        _warning(
                            ValidationSeverity.WARNING,
                            "tree_grammar_parent_type_not_allowed",
                            (
                                f"node_type '{node_type.value}' may not attach to parent "
                                f"of type '{parent_type.value}'."
                            ),
                            related_item_id=context.item_id,
                            related_tree_node_id=node["tree_node_id"],
                        )
                    )

        # Leaf rule: leaf types must not have children.
        children_count: dict[str, int] = {nid: 0 for nid in nodes_by_id}
        for node in nodes_by_id.values():
            parent_id = node["parent_node_id"]
            if parent_id is not None:
                children_count[parent_id] = children_count.get(parent_id, 0) + 1
        for nid, count in children_count.items():
            node = nodes_by_id[nid]
            if count > 0 and node["node_type"] in LEAF_NODE_TYPES:
                warnings.append(
                    _warning(
                        ValidationSeverity.WARNING,
                        "tree_grammar_leaf_has_children",
                        f"Leaf node_type '{node['node_type'].value}' has children.",
                        related_item_id=context.item_id,
                        related_tree_node_id=nid,
                    )
                )

        # Build EvidenceTreeNode instances.
        tree_nodes: list[EvidenceTreeNode] = []
        mapped_assertion_ids: set[str] = set()
        for nid, node in nodes_by_id.items():
            try:
                tree_node = EvidenceTreeNode(
                    tree_node_id=node["tree_node_id"],
                    source_item_id=context.item_id,
                    node_type=node["node_type"],
                    node_text=node["node_text"],
                    assertion_status=node["assertion_status"],
                    certainty=node["certainty"],
                    temporality=node["temporality"],
                    parent_node_id=node["parent_node_id"],
                    relation_to_parent=node["relation_to_parent"],
                    inherited_context_node_ids=node["inherited_context_node_ids"],
                    source_assertion_ids=node["source_assertion_ids"],
                    source_attribute_ids=[],
                    source_span_ids=node["source_span_ids"],
                    node_origin=node["node_origin"],
                    context_role=node["context_role"],
                    confidence=node["confidence"],
                    notes=node.get("notes"),
                )
            except ValidationError as exc:
                warnings.append(
                    _warning(
                        ValidationSeverity.WARNING,
                        "tree_node_validation_failed",
                        f"Node validation failed: {exc.errors()[0].get('msg', '?')}",
                        related_item_id=context.item_id,
                    )
                )
                continue
            tree_nodes.append(tree_node)
            mapped_assertion_ids.update(tree_node.source_assertion_ids)

        if not tree_nodes:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "tree_payload_all_nodes_invalid",
                    "All nodes failed pydantic validation.",
                    related_item_id=context.item_id,
                )
            )
            return None, warnings

        # Assertion mapping coverage.
        deferred_raw = payload.get("deferred_assertion_ids", []) or []
        deferred = [
            str(value).strip()
            for value in deferred_raw
            if isinstance(value, str) and value.strip() in valid_assertion_ids
        ]
        unmapped = (
            valid_assertion_ids - mapped_assertion_ids - set(deferred)
        )
        for assertion_id in unmapped:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "tree_assertion_mapping_missing",
                    f"ClinicalObjectAssertion '{assertion_id}' is neither mapped to a tree node nor deferred.",
                    related_item_id=context.item_id,
                )
            )

        # Degenerate-tree checks.
        if len(tree_nodes) == 1 and assertions:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "degenerate_tree_single_node",
                    "Tree collapsed to a single node despite multiple assertions.",
                    related_item_id=context.item_id,
                )
            )
        if (
            assertions
            and len(tree_nodes) > 0
            and len(mapped_assertion_ids) == len(assertions)
            and len({node.tree_node_id for node in tree_nodes if node.source_assertion_ids}) == 1
            and len(assertions) > 1
        ):
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "degenerate_tree_assertions_collapsed",
                    "All assertions were collapsed into one assertion-backed node.",
                    related_item_id=context.item_id,
                )
            )

        # Forward LLM-emitted tree_warnings that parse cleanly.
        for raw_warning in payload.get("tree_warnings", []) or []:
            if not isinstance(raw_warning, dict):
                continue
            try:
                warnings.append(TreeStructuringWarning(**raw_warning))
            except ValidationError:
                continue

        try:
            tree = EvidenceTree(
                source_item_id=context.item_id,
                source_text=context.source_text,
                tree_nodes=tree_nodes,
                deferred_assertion_ids=deferred,
                tree_warnings=[],
            )
        except ValidationError as exc:
            warnings.append(
                _warning(
                    ValidationSeverity.ERROR,
                    "tree_pydantic_validation_failed",
                    f"EvidenceTree pydantic validation failed: {exc.errors()[0].get('msg', '?')}",
                    related_item_id=context.item_id,
                )
            )
            return None, warnings

        return tree, warnings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _coerce_node(
    raw: dict[str, Any],
    *,
    context: ItemContext,
    valid_assertion_ids: set[str],
    valid_span_ids: set[str],
) -> tuple[dict[str, Any] | None, str]:
    node_text = _str(raw.get("node_text"))
    if not node_text:
        return None, "node_text is empty"
    if node_text not in context.source_text:
        return None, "node_text is not a substring of source_text"

    node_type = _enum(
        raw.get("node_type"),
        EvidenceTreeNodeType,
        default=EvidenceTreeNodeType.UNCERTAIN_OR_OTHER,
    )

    assertion_status = _enum(
        raw.get("assertion_status"),
        NegationStatus,
        default=NegationStatus.PRESENT,
    )
    certainty = _enum(
        raw.get("certainty"),
        CertaintyLevel,
        default=CertaintyLevel.UNKNOWN,
    )
    temporality = _enum(
        raw.get("temporality"),
        TemporalRelation,
        default=TemporalRelation.UNKNOWN,
    )
    relation = _enum(
        raw.get("relation_to_parent"),
        EvidenceTreeRelationType,
        default=EvidenceTreeRelationType.OTHER_RELATION,
    )
    node_origin = _enum(
        raw.get("node_origin"),
        EvidenceTreeNodeOrigin,
        default=EvidenceTreeNodeOrigin.CONTEXT_BACKED,
    )
    context_role = _enum(
        raw.get("context_role"),
        ContextRole,
        default=ContextRole.LOCAL_CONTENT,
    )
    confidence = _enum(
        raw.get("confidence"),
        ConfidenceLevel,
        default=ConfidenceLevel.MEDIUM,
    )

    source_assertion_ids: list[str] = []
    for sid in raw.get("source_assertion_ids", []) or []:
        cleaned = _str(sid)
        if (
            cleaned is not None
            and cleaned in valid_assertion_ids
            and cleaned not in source_assertion_ids
        ):
            source_assertion_ids.append(cleaned)

    source_span_ids: list[str] = []
    for sid in raw.get("source_span_ids", []) or []:
        cleaned = _str(sid)
        if (
            cleaned is not None
            and cleaned in valid_span_ids
            and cleaned not in source_span_ids
        ):
            source_span_ids.append(cleaned)
    if not source_span_ids and context.span_ids:
        source_span_ids = list(context.span_ids)

    # Coerce node_origin against grounding.
    if node_origin == EvidenceTreeNodeOrigin.ASSERTION_BACKED and not source_assertion_ids:
        node_origin = EvidenceTreeNodeOrigin.CONTEXT_BACKED
    if node_origin != EvidenceTreeNodeOrigin.ASSERTION_BACKED and source_assertion_ids:
        node_origin = EvidenceTreeNodeOrigin.ASSERTION_BACKED
    if node_origin == EvidenceTreeNodeOrigin.CONTEXT_BACKED and not source_span_ids:
        return None, "context_backed node has no source_span_ids"

    parent_raw = _str(raw.get("parent_raw_id"))
    inherited_raw_ids: list[str] = []
    for ctx_id in raw.get("inherited_context_raw_ids", []) or []:
        cleaned = _str(ctx_id)
        if cleaned is not None and cleaned not in inherited_raw_ids:
            inherited_raw_ids.append(cleaned)

    return (
        {
            "node_type": node_type,
            "node_text": node_text,
            "assertion_status": assertion_status,
            "certainty": certainty,
            "temporality": temporality,
            "relation_to_parent": relation,
            "node_origin": node_origin,
            "context_role": context_role,
            "confidence": confidence,
            "source_assertion_ids": source_assertion_ids,
            "source_span_ids": source_span_ids,
            "notes": _str(raw.get("notes")),
            "_parent_raw": parent_raw,
            "_inherited_raw": inherited_raw_ids,
        },
        "",
    )


def _detect_cycle_node_ids(
    nodes_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    cycle_ids: list[str] = []
    for start_id in nodes_by_id:
        visited: set[str] = set()
        current: str | None = start_id
        depth = 0
        while current is not None:
            if current in visited:
                cycle_ids.append(start_id)
                break
            visited.add(current)
            current = nodes_by_id.get(current, {}).get("parent_node_id")
            depth += 1
            if depth > len(nodes_by_id) + 1:
                cycle_ids.append(start_id)
                break
    return list(dict.fromkeys(cycle_ids))


def _str(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return None


def _enum(value: Any, enum_type: type, default: Any) -> Any:
    if isinstance(value, str):
        try:
            return enum_type(value.strip())
        except ValueError:
            return default
    return default


def _warning(
    severity: ValidationSeverity,
    code: str,
    message: str,
    *,
    related_item_id: str | None = None,
    related_tree_node_id: str | None = None,
    related_span_id: str | None = None,
) -> TreeStructuringWarning:
    return TreeStructuringWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_tree_node_id=related_tree_node_id,
        related_span_id=related_span_id,
    )
