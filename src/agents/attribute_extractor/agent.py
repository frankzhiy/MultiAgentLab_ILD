from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.attribute_extractor.pipeline import AttributeExtractorPipeline
from src.agents.attribute_extractor.result import AttributeExtractionValidationResult
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


class AttributeExtractorAgent:
    """Public Attribute Extractor facade backed by an internal hybrid pipeline."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "attribute_extractor",
    ) -> None:
        self.pipeline = AttributeExtractorPipeline(
            llm_client=llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        structuring_result: CaseStructuringResult,
    ) -> AttributeExtractionResult:
        return self.pipeline.run(structuring_result)

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
    ) -> AttributeExtractionValidationResult:
        return self.pipeline.run_with_validation(structuring_result)
