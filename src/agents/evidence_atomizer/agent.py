from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.evidence_atomizer.pipeline import EvidenceAtomizerPipeline
from src.agents.evidence_atomizer.result import EvidenceAtomizationValidationResult
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


class EvidenceAtomizerAgent:
    """Public Evidence Atomizer facade backed by an internal hybrid pipeline."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_atomizer",
    ) -> None:
        self.pipeline = EvidenceAtomizerPipeline(
            llm_client=llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        structuring_result: CaseStructuringResult,
    ) -> EvidenceAtomizationResult:
        return self.pipeline.run(structuring_result)

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
    ) -> EvidenceAtomizationValidationResult:
        return self.pipeline.run_with_validation(structuring_result)
