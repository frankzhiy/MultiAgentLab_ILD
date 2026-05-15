from __future__ import annotations

from src.agents.evidence_atomizer.modules.evidence_atom_normalizer import (
    NormalizedEvidenceAtomizationPayload,
)
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_atomizer.common import ValidationSeverity
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)


class EvidenceAtomizationAssembler:
    """Assemble normalized atomization objects into the final result package."""

    def assemble(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        normalized_payload: NormalizedEvidenceAtomizationPayload,
    ) -> EvidenceAtomizationResult:
        _ = attribute_result
        has_error_warning = any(
            warning.severity == ValidationSeverity.ERROR
            for warning in normalized_payload.atomization_warnings
        )
        ready_for_hypothesis_state = (
            bool(normalized_payload.evidence_atoms) and not has_error_warning
        )

        return EvidenceAtomizationResult(
            case_id=structuring_result.input.case_id,
            input_id=structuring_result.input.input_id,
            stage_id=structuring_result.stage_context.stage_id,
            source_structuring_result_id=(
                structuring_result.case_structuring_result_id
            ),
            evidence_atoms=normalized_payload.evidence_atoms,
            item_to_evidence_links=normalized_payload.item_to_evidence_links,
            deferred_items=normalized_payload.deferred_items,
            atomization_warnings=normalized_payload.atomization_warnings,
            ready_for_hypothesis_state=ready_for_hypothesis_state,
        )
