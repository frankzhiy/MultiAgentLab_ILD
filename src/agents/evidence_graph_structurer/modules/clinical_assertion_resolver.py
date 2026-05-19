"""Clinical Assertion Resolver — LLM #1 of the Evidence Graph Structurer.

For each ItemContext, prompt the LLM once to produce ClinicalObjectAssertions
strictly conforming to the ClinicalObjectAssertion schema. The result is
validated and source-grounded by ClinicalAssertionValidator.
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)

from ..prompting import (
    assertion_issue_fields,
    clinical_assertion_output_skeleton,
    clinical_object_assertion_fields,
    format_forbidden_downstream_objects,
    format_graph_structuring_boundary,
    format_item_context,
)
from .base_llm_extractor import BaseLLMExtractor
from .clinical_assertion_validator import ClinicalAssertionValidator
from .item_context import ItemContext

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


_INSTRUCTION = (
    "Extract source-grounded ClinicalObjectAssertion records for the provided "
    "StructuredClinicalItem. Your output must strictly conform to the JSON schema "
    "defined for ClinicalObjectAssertion — include only the fields declared in the "
    "schema and populate every required field. Frame grouping and inter-object "
    "relations are handled by separate downstream components and must not appear "
    "in your output."
)


class ClinicalAssertionResolver:
    """LLM-driven resolver from ItemContext to ClinicalObjectAssertion list."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "evidence_graph_structurer",
    ) -> None:
        self.extractor = BaseLLMExtractor(llm_client, agent_name=agent_name)
        self.validator = ClinicalAssertionValidator()

    def resolve(
        self,
        contexts: list[ItemContext],
    ) -> ClinicalAssertionResolutionResult:
        all_assertions = []
        all_issues: list[EvidenceStructuringIssue] = []
        for context in contexts:
            result = self._resolve_one(context)
            all_assertions.extend(result.clinical_object_assertions)
            all_issues.extend(result.assertion_issues)
        return ClinicalAssertionResolutionResult(
            clinical_object_assertions=all_assertions,
            assertion_issues=all_issues,
        )

    def _resolve_one(self, context: ItemContext) -> ClinicalAssertionResolutionResult:
        prompt_path = self.extractor.prompt_path("clinical_assertion_labeling")
        item_context_str = format_item_context(context)
        template_vars = {
            "graph_structuring_boundary": format_graph_structuring_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "item_context": item_context_str,
            "clinical_object_assertion_fields": clinical_object_assertion_fields(),
            "assertion_issue_fields": assertion_issue_fields(),
            "clinical_assertion_output_skeleton": clinical_assertion_output_skeleton(),
        }
        user_payload: dict[str, Any] = {
            "item_id": context.item_id,
            "source_text": context.source_text,
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
            return ClinicalAssertionResolutionResult(
                clinical_object_assertions=[],
                assertion_issues=[
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.ERROR,
                        code="clinical_assertion_llm_invalid_json",
                        message=(
                            "LLM returned non-JSON content for clinical assertion "
                            f"labeling: {exc.msg}"
                        ),
                        related_item_id=context.item_id,
                    )
                ],
            )

        if not isinstance(payload, dict):
            return ClinicalAssertionResolutionResult(
                clinical_object_assertions=[],
                assertion_issues=[
                    EvidenceStructuringIssue(
                        severity=ValidationSeverity.ERROR,
                        code="clinical_assertion_llm_unexpected_shape",
                        message="LLM payload is not a JSON object.",
                        related_item_id=context.item_id,
                    )
                ],
            )

        return self.validator.validate(context, payload)
