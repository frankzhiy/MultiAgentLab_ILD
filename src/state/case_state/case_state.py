"""Minimal shared case state."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.evidence_tree_structurer.evidence_tree_structuring_result import (
    EvidenceTreeStructuringResult,
)
from src.schemas.evidence_tree_structurer.evidence_tree import EvidenceTree
from src.state.write_event import WriteEvent
from src.validators.case_structurer import CaseStructuringSourceSpanResult


class CaseState(BaseModel):
    """In-memory shared state for one case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    raw_inputs: list[RawTextInput] = Field(default_factory=list)
    case_structuring_results: list[CaseStructuringResult] = Field(
        default_factory=list
    )
    evidence_tree_structuring_results: list[EvidenceTreeStructuringResult] = Field(
        default_factory=list
    )
    evidence_trees: list[EvidenceTree] = Field(default_factory=list)
    case_structuring_source_span_results: list[
        CaseStructuringSourceSpanResult
    ] = Field(default_factory=list)
    write_events: list[WriteEvent] = Field(default_factory=list)

    def has_input(self, input_id: str) -> bool:
        """Return whether this state already stores the raw input."""
        return any(raw_input.input_id == input_id for raw_input in self.raw_inputs)

    def has_case_structuring_result(self, input_id: str) -> bool:
        """Return whether this state already stores a structuring result."""
        return any(
            result.input.input_id == input_id
            for result in self.case_structuring_results
        )

    def has_evidence_tree_structuring_result(self, input_id: str) -> bool:
        """Return whether this state already stores an tree structuring result."""
        return any(
            result.input_id == input_id
            for result in self.evidence_tree_structuring_results
        )
