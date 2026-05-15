from __future__ import annotations

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_atomizer.atomization_warning import AtomizationWarning
from src.schemas.evidence_atomizer.common import ValidationSeverity


class EvidenceAtomizerInputGuard:
    """Deterministic preflight checks before LLM evidence atomization."""

    def check(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
    ) -> list[AtomizationWarning]:
        warnings: list[AtomizationWarning] = []

        if structuring_result.input.case_id != attribute_result.case_id:
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="case_id_mismatch",
                    message=(
                        "CaseStructuringResult case_id must match "
                        "AttributeExtractionResult.case_id."
                    ),
                )
            )

        if structuring_result.input.input_id != attribute_result.input_id:
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="input_id_mismatch",
                    message=(
                        "CaseStructuringResult input_id must match "
                        "AttributeExtractionResult.input_id."
                    ),
                )
            )

        if (
            attribute_result.source_structuring_result_id
            != structuring_result.case_structuring_result_id
        ):
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="source_structuring_result_id_mismatch",
                    message=(
                        "AttributeExtractionResult.source_structuring_result_id "
                        "must match CaseStructuringResult.case_structuring_result_id."
                    ),
                )
            )

        if not structuring_result.ready_for_attribute_extraction:
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="structuring_result_not_ready",
                    message=(
                        "Case structuring result is not ready for evidence "
                        "atomization."
                    ),
                )
            )

        if not attribute_result.ready_for_evidence_atomization:
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="attribute_result_not_ready",
                    message=(
                        "Attribute extraction result is not ready for evidence "
                        "atomization."
                    ),
                )
            )

        if not structuring_result.structured_items:
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="no_structured_items",
                    message=(
                        "Case structuring result contains no structured "
                        "clinical items to atomize."
                    ),
                )
            )

        for item in structuring_result.structured_items:
            if item.source_spans:
                continue
            warnings.append(
                AtomizationWarning(
                    severity=ValidationSeverity.ERROR,
                    code="item_missing_source_spans",
                    message=(
                        "Structured clinical item has no source spans and "
                        "cannot be atomized safely."
                    ),
                    related_item_id=item.item_id,
                )
            )

        return warnings
