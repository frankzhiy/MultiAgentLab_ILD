from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.evidence_atomizer import ClinicalAssertionResolutionResult
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)
from src.validators.evidence_atomizer import EvidenceAtomizationValidationReport


class EvidenceAtomizationValidationResult(BaseModel):
    """Evidence Atomizer output plus deterministic validation report."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    atomization_result: EvidenceAtomizationResult = Field(
        ...,
        description="Evidence Atomizer result produced by the pipeline.",
    )
    validation_report: EvidenceAtomizationValidationReport = Field(
        ...,
        description="Deterministic validation report for the atomization result.",
    )
    clinical_assertion_resolution: ClinicalAssertionResolutionResult = Field(
        default_factory=ClinicalAssertionResolutionResult,
        description="Internal object-level clinical assertion resolution payload.",
    )

    @property
    def accepted(self) -> bool:
        """Return whether deterministic validation accepted the result."""
        return self.validation_report.accepted
