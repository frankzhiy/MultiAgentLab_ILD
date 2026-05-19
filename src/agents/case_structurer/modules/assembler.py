from __future__ import annotations

from src.schemas.case_structurer.case_structuring_result import (
    CaseStructuringResult,
    StructuringWarning,
)
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import StageContext
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem


class CaseStructuringAssembler:
    """Assemble the final schema object without another LLM call."""

    def assemble(
        self,
        raw_input: RawTextInput,
        stage_context: StageContext,
        sections: list[ClinicalSection],
        items: list[StructuredClinicalItem],
    ) -> CaseStructuringResult:
        warnings: list[StructuringWarning] = []
        ready_for_evidence_graph_structuring = bool(sections or items)

        if not ready_for_evidence_graph_structuring:
            warnings.append(
                StructuringWarning(
                    severity=ValidationSeverity.WARNING,
                    code="missing_clinical_structure",
                    message=(
                        "No clinical sections or structured clinical items were "
                        "produced from this input."
                    ),
                    related_object_id=raw_input.input_id,
                )
            )

        return CaseStructuringResult(
            input=raw_input,
            stage_context=stage_context,
            clinical_sections=sections,
            structured_items=items,
            structuring_warnings=warnings,
            ready_for_evidence_graph_structuring=ready_for_evidence_graph_structuring,
        )
