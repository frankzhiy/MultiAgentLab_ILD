from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from src.agents.evidence_tree_structurer.pipeline import EvidenceTreeStructurerPipeline
from src.agents.evidence_tree_structurer.result import EvidenceTreeStructuringValidationResult
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_tree_structurer.evidence_tree_structuring_result import (
    EvidenceTreeStructuringResult,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


class EvidenceTreeStructurerAgent:
    """Public Evidence Tree Structurer facade backed by an internal hybrid pipeline."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_tree_structurer",
    ) -> None:
        self.pipeline = EvidenceTreeStructurerPipeline(
            llm_client=llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceTreeStructuringResult:
        return self.pipeline.run(
            structuring_result,
            progress_callback=progress_callback,
        )

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceTreeStructuringValidationResult:
        return self.pipeline.run_with_validation(
            structuring_result,
            progress_callback=progress_callback,
        )
