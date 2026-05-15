from __future__ import annotations

from typing import Any

from src.agents.attribute_extractor.prompting.output_skeletons import (
    attribute_span_role_labeling_skeleton,
)
from src.agents.attribute_extractor.prompting.prompt_context import (
    build_attribute_item_payload,
    format_attribute_boundary,
    format_attribute_items,
)
from src.agents.attribute_extractor.prompting.schema_contracts import (
    attribute_span_role_labeling_contract,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

from .base_llm_extractor import BaseLLMExtractor


class AttributeSpanRoleExtractor(BaseLLMExtractor):
    """LLM target-grounded attribute relation labeler for source item text."""

    def extract(self, structuring_result: CaseStructuringResult) -> dict[str, Any]:
        item_payload = build_attribute_item_payload(structuring_result)
        template_vars = {
            **attribute_span_role_labeling_contract(),
            "case_id": structuring_result.input.case_id,
            "input_id": structuring_result.input.input_id,
            "case_structuring_result_id": (
                structuring_result.case_structuring_result_id
            ),
            "attribute_boundary": format_attribute_boundary(),
            "attribute_items": format_attribute_items(item_payload),
            "output_skeleton": attribute_span_role_labeling_skeleton(),
        }

        content = self.generate_json(
            prompt_path=self.prompt_path("attribute_span_role_labeling"),
            user_payload={
                "case_id": structuring_result.input.case_id,
                "input_id": structuring_result.input.input_id,
                "case_structuring_result_id": (
                    structuring_result.case_structuring_result_id
                ),
                "structured_items": item_payload,
            },
            instruction=(
                "Return exactly one JSON object with keys attribute_spans and "
                "extraction_warnings. Do not output context_text."
            ),
            template_vars=template_vars,
            response_format="json_object",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("Attribute relation payload must be a JSON object.")

        for key in ("attribute_spans", "extraction_warnings"):
            if key not in payload:
                payload[key] = []
            if not isinstance(payload[key], list):
                raise ValueError(f"Attribute payload key {key!r} must be an array.")

        return payload
