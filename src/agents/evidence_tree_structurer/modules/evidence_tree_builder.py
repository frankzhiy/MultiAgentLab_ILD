"""EvidenceTreeBuilder — LLM #2 of the Evidence Tree Structurer.

For each ItemContext + its ClinicalObjectAssertions, prompt the LLM to build
one EvidenceTree, validate the response, retry once on failure, and fall back
to a single ``uncertain_or_other`` node with an ERROR warning if the retry
also fails.
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

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
    ContextRole,
    EvidenceTree,
    EvidenceTreeBuildResult,
    EvidenceTreeNode,
    EvidenceTreeNodeOrigin,
    EvidenceTreeNodeType,
    EvidenceTreeRelationType,
)
from src.schemas.evidence_tree_structurer.tree_structuring_warning import (
    TreeStructuringWarning,
)
from src.utils.id_generator import generate_evidence_tree_node_id

from ..prompting import (
    evidence_tree_grammar_summary,
    evidence_tree_node_fields,
    evidence_tree_output_skeleton,
    format_clinical_object_assertions,
    format_forbidden_downstream_objects,
    format_item_context,
    format_tree_structuring_boundary,
)
from .base_llm_extractor import BaseLLMExtractor
from .evidence_tree_validator import EvidenceTreeValidator
from .item_context import ItemContext

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


_INSTRUCTION = (
    "Build a typed EvidenceTree for the provided StructuredClinicalItem using "
    "its source_text and the ClinicalObjectAssertion list. Decide parent/child "
    "structure yourself from the assertions and source text — there are no "
    "pre-computed parent hints. Follow the node-grammar and source-grounding "
    "rules in the system prompt. Return strict JSON matching the contract."
)


class EvidenceTreeBuilder:
    """LLM-driven builder from (ItemContext, assertions) to EvidenceTree."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "evidence_tree_structurer",
        max_attempts: int = 2,
    ) -> None:
        self.extractor = BaseLLMExtractor(llm_client, agent_name=agent_name)
        self.validator = EvidenceTreeValidator()
        self.max_attempts = max_attempts

    def build(
        self,
        contexts: list[ItemContext],
        assertions: list[ClinicalObjectAssertion],
    ) -> EvidenceTreeBuildResult:
        assertions_by_item: dict[str, list[ClinicalObjectAssertion]] = {}
        for assertion in assertions:
            assertions_by_item.setdefault(assertion.source_item_id, []).append(
                assertion
            )

        trees: list[EvidenceTree] = []
        warnings: list[TreeStructuringWarning] = []
        for context in contexts:
            item_assertions = assertions_by_item.get(context.item_id, [])
            tree, item_warnings = self._build_one(context, item_assertions)
            warnings.extend(item_warnings)
            if tree is not None:
                trees.append(tree)

        return EvidenceTreeBuildResult(evidence_trees=trees, warnings=warnings)

    def _build_one(
        self,
        context: ItemContext,
        assertions: list[ClinicalObjectAssertion],
    ) -> tuple[EvidenceTree | None, list[TreeStructuringWarning]]:
        collected_warnings: list[TreeStructuringWarning] = []
        prompt_path = self.extractor.prompt_path("evidence_tree_building")
        item_context_str = format_item_context(context)
        template_vars = {
            "tree_structuring_boundary": format_tree_structuring_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "item_context": item_context_str,
            "clinical_object_assertions": format_clinical_object_assertions(assertions),
            "evidence_tree_node_fields": evidence_tree_node_fields(),
            "evidence_tree_grammar_summary": evidence_tree_grammar_summary(),
            "evidence_tree_output_skeleton": evidence_tree_output_skeleton(context.item_id),
        }
        user_payload: dict[str, Any] = {
            "item_id": context.item_id,
            "source_text": context.source_text,
        }

        for attempt in range(1, self.max_attempts + 1):
            payload, attempt_warnings = self._call_llm(
                context=context,
                prompt_path=prompt_path,
                user_payload=user_payload,
                template_vars=template_vars,
                attempt=attempt,
            )
            collected_warnings.extend(attempt_warnings)
            if payload is None:
                continue
            tree, validator_warnings = self.validator.validate(
                context=context,
                payload=payload,
                assertions=assertions,
            )
            collected_warnings.extend(validator_warnings)
            has_error = any(
                w.severity == ValidationSeverity.ERROR for w in validator_warnings
            )
            if tree is not None and not has_error:
                return tree, collected_warnings

        # All attempts failed — emit a single uncertain_or_other fallback tree
        # plus an ERROR warning per user option (a).
        collected_warnings.append(
            TreeStructuringWarning(
                severity=ValidationSeverity.ERROR,
                code="tree_build_fallback_uncertain",
                message=(
                    f"Evidence tree builder failed after {self.max_attempts} attempts; "
                    "emitted a single uncertain_or_other fallback node."
                ),
                related_item_id=context.item_id,
            )
        )
        fallback = _fallback_tree(context, assertions)
        return fallback, collected_warnings

    def _call_llm(
        self,
        *,
        context: ItemContext,
        prompt_path: str,
        user_payload: dict[str, Any],
        template_vars: dict[str, Any],
        attempt: int,
    ) -> tuple[dict[str, Any] | None, list[TreeStructuringWarning]]:
        try:
            raw_content = self.extractor.generate_json(
                prompt_path=prompt_path,
                user_payload=user_payload,
                instruction=_INSTRUCTION,
                template_vars=template_vars,
            )
            payload = self.extractor.parse_json_content(raw_content)
        except JSONDecodeError as exc:
            return None, [
                TreeStructuringWarning(
                    severity=ValidationSeverity.WARNING,
                    code="tree_llm_invalid_json",
                    message=(
                        f"Attempt {attempt}: LLM returned non-JSON content: {exc.msg}"
                    ),
                    related_item_id=context.item_id,
                )
            ]

        if not isinstance(payload, dict):
            return None, [
                TreeStructuringWarning(
                    severity=ValidationSeverity.WARNING,
                    code="tree_llm_unexpected_shape",
                    message=f"Attempt {attempt}: LLM payload is not a JSON object.",
                    related_item_id=context.item_id,
                )
            ]
        return payload, []


def _fallback_tree(
    context: ItemContext,
    assertions: list[ClinicalObjectAssertion],
) -> EvidenceTree | None:
    """Build a single-node uncertain_or_other tree as a last resort."""

    span_ids = list(context.span_ids) or []
    node_text = (context.source_text or context.label or context.item_id).strip()
    if not node_text:
        return None

    try:
        node = EvidenceTreeNode(
            tree_node_id=generate_evidence_tree_node_id(),
            source_item_id=context.item_id,
            node_type=EvidenceTreeNodeType.UNCERTAIN_OR_OTHER,
            node_text=node_text[:200] if node_text else context.item_id,
            assertion_status=NegationStatus.UNKNOWN,
            certainty=CertaintyLevel.UNKNOWN,
            temporality=TemporalRelation.UNKNOWN,
            parent_node_id=None,
            relation_to_parent=EvidenceTreeRelationType.ROOT_OF,
            inherited_context_node_ids=[],
            source_assertion_ids=[],
            source_attribute_ids=[],
            source_span_ids=span_ids,
            node_origin=EvidenceTreeNodeOrigin.STRUCTURAL_GROUP,
            context_role=ContextRole.UNCERTAIN,
            confidence=ConfidenceLevel.LOW,
            notes="Fallback after evidence tree build retries failed.",
        )
    except ValidationError:
        return None

    try:
        return EvidenceTree(
            source_item_id=context.item_id,
            source_text=context.source_text or context.item_id,
            tree_nodes=[node],
            deferred_assertion_ids=[a.object_id for a in assertions],
            tree_warnings=[],
        )
    except ValidationError:
        return None
