from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from src.agents.evidence_graph_structurer.pipeline import (
    EvidenceGraphStructurerPipeline,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_graph_structurer.evidence_structuring_result import (
    EvidenceStructuringResult,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


class EvidenceGraphStructurerAgent:
    """Public Evidence Graph Structurer facade backed by an internal pipeline."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_graph_structurer",
    ) -> None:
        self.pipeline = EvidenceGraphStructurerPipeline(
            llm_client=llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceStructuringResult:
        return self.pipeline.run(
            structuring_result,
            progress_callback=progress_callback,
        )
