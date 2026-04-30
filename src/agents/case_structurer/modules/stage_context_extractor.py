from __future__ import annotations

from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import (
    StageContext,
    StageRelation,
    StageType,
)

from .base_llm_extractor import BaseLLMExtractor


class StageContextExtractor(BaseLLMExtractor):
    """Extract workflow-level stage context without clinical facts."""

    def extract(self, raw_input: RawTextInput) -> StageContext:
        content = self.generate_json(
            prompt_path=self.prompt_path("stage_context"),
            user_payload={"raw_input": raw_input.model_dump(mode="json")},
            instruction="Return exactly one StageContext JSON object.",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("StageContext extractor returned a non-object JSON value.")

        stage_order = raw_input.input_order or 1
        is_initial_stage = stage_order == 1

        stage_type = payload.get("stage_type") or StageType.UNKNOWN
        if is_initial_stage and stage_type not in {
            StageType.INITIAL_INPUT,
            StageType.UNKNOWN,
            StageType.INITIAL_INPUT.value,
            StageType.UNKNOWN.value,
        }:
            stage_type = StageType.UNKNOWN

        relation = payload.get("relation_to_previous_stage") or StageRelation.UNKNOWN
        if is_initial_stage:
            relation = StageRelation.NEW_CASE_START
        elif relation in {
            StageRelation.NEW_CASE_START,
            StageRelation.NEW_CASE_START.value,
        }:
            relation = StageRelation.UNKNOWN

        final_payload = {
            "case_id": raw_input.case_id,
            "input_id": raw_input.input_id,
            "stage_order": stage_order,
            "stage_type": stage_type,
            "relation_to_previous_stage": relation,
            "previous_stage_id": None,
            "is_initial_stage": is_initial_stage,
            "classification_confidence": (
                payload.get("classification_confidence") or "medium"
            ),
            "classification_basis": payload.get("classification_basis"),
        }
        return StageContext.model_validate(final_payload)
