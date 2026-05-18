from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.evidence_tree_structurer import ClinicalAssertionResolutionResult
from src.schemas.evidence_tree_structurer.evidence_tree_structuring_result import (
    EvidenceTreeStructuringResult,
)
from src.schemas.evidence_tree_structurer.evidence_tree import (
    EvidenceTreeBuildResult,
)
from src.validators.evidence_tree_structurer import EvidenceTreeStructuringValidationReport


class EvidenceTreeStructuringValidationResult(BaseModel):
    """Evidence Tree Structurer output plus deterministic validation report."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    tree_structuring_result: EvidenceTreeStructuringResult = Field(
        ...,
        description="Evidence Tree Structurer result produced by the pipeline.",
    )
    validation_report: EvidenceTreeStructuringValidationReport = Field(
        ...,
        description="Deterministic validation report for the tree structuring result.",
    )
    clinical_assertion_resolution: ClinicalAssertionResolutionResult = Field(
        default_factory=ClinicalAssertionResolutionResult,
        description="Internal object-level clinical assertion resolution payload.",
    )
    evidence_tree_build_result: EvidenceTreeBuildResult = Field(
        default_factory=EvidenceTreeBuildResult,
        description="Internal EvidenceTree construction debug payload.",
    )
    pipeline_timings_seconds: dict[str, float] = Field(
        default_factory=dict,
        description="Per-step Evidence Tree Structurer pipeline timings in seconds.",
    )

    @property
    def accepted(self) -> bool:
        """Return whether deterministic validation accepted the result."""
        return self.validation_report.accepted
