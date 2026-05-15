"""Minimal shared case state."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.attribute_extractor.clinical_attribute import ClinicalAttribute
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.evidence_atomizer.evidence_atom import EvidenceAtom
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)
from src.state.write_event import WriteEvent
from src.validators.case_structurer import SourceSpanValidationCorrectionResult


class CaseState(BaseModel):
    """In-memory shared state for one case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    raw_inputs: list[RawTextInput] = Field(default_factory=list)
    case_structuring_results: list[CaseStructuringResult] = Field(
        default_factory=list
    )
    attribute_extraction_results: list[AttributeExtractionResult] = Field(
        default_factory=list
    )
    evidence_atomization_results: list[EvidenceAtomizationResult] = Field(
        default_factory=list
    )
    clinical_attributes: list[ClinicalAttribute] = Field(default_factory=list)
    evidence_atoms: list[EvidenceAtom] = Field(default_factory=list)
    source_span_validation_correction_results: list[
        SourceSpanValidationCorrectionResult
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

    def has_attribute_extraction_result(self, input_id: str) -> bool:
        """Return whether this state already stores an attribute result."""
        return any(
            result.input_id == input_id
            for result in self.attribute_extraction_results
        )

    def has_evidence_atomization_result(self, input_id: str) -> bool:
        """Return whether this state already stores an atomization result."""
        return any(
            result.input_id == input_id
            for result in self.evidence_atomization_results
        )
