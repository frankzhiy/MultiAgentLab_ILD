from __future__ import annotations

from src.agents.case_structurer.pipeline import CaseStructurerPipeline
from src.llm.chatanywhere_client import ChatAnywhereClient
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


class CaseStructurerAgent:
    """Public Case Structurer facade backed by the internal Scheme C pipeline."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "case_structurer",
    ) -> None:
        self.pipeline = CaseStructurerPipeline(
            llm_client=llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringResult:
        return self.pipeline.run(
            raw_text=raw_text,
            case_id=case_id,
            input_order=input_order,
            parent_input_id=parent_input_id,
        )
