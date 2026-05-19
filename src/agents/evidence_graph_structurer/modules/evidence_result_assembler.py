"""Evidence Result Assembler — deterministic, no LLM."""

from __future__ import annotations

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
)
from src.schemas.evidence_graph_structurer.evidence_graph_validation import (
    EvidenceGraphValidationReport,
    EvidenceGraphValidationStatus,
)
from src.schemas.evidence_graph_structurer.evidence_graphlet import (
    EvidenceGraphlet,
    EvidenceGraphletStatus,
)
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)
from src.schemas.evidence_graph_structurer.evidence_structuring_result import (
    EvidenceStructuringResult,
)


_STATUS_MAP = {
    EvidenceGraphValidationStatus.ACCEPTED: EvidenceGraphletStatus.ACCEPTED,
    EvidenceGraphValidationStatus.REJECTED: EvidenceGraphletStatus.REJECTED,
    EvidenceGraphValidationStatus.NEEDS_REVIEW: EvidenceGraphletStatus.NEEDS_REVIEW,
}


class EvidenceResultAssembler:
    """Assemble the final EvidenceStructuringResult."""

    def assemble(
        self,
        case_structuring_result: CaseStructuringResult,
        assertion_result: ClinicalAssertionResolutionResult,
        graphlets: list[EvidenceGraphlet],
        reports: list[EvidenceGraphValidationReport],
        extra_issues: list[EvidenceStructuringIssue],
        timings: dict[str, float],
    ) -> EvidenceStructuringResult:
        report_by_graphlet = {report.graphlet_id: report for report in reports}

        updated_graphlets: list[EvidenceGraphlet] = []
        for graphlet in graphlets:
            report = report_by_graphlet.get(graphlet.graphlet_id)
            if report is None:
                updated_graphlets.append(graphlet)
                continue
            updated_graphlets.append(
                graphlet.model_copy(
                    update={
                        "status": _STATUS_MAP.get(
                            report.status, EvidenceGraphletStatus.NEEDS_REVIEW
                        ),
                        "validation_report_id": report.validation_report_id,
                    }
                )
            )

        ready_for_hypothesis_state = bool(updated_graphlets) and all(
            report.downstream_readiness for report in reports
        )

        return EvidenceStructuringResult(
            case_id=case_structuring_result.input.case_id,
            input_id=case_structuring_result.input.input_id,
            stage_id=case_structuring_result.stage_context.stage_id,
            source_structuring_result_id=(
                case_structuring_result.case_structuring_result_id
                if hasattr(case_structuring_result, "case_structuring_result_id")
                else None
            ),
            clinical_object_assertions=assertion_result.clinical_object_assertions,
            assertion_issues=assertion_result.assertion_issues,
            graphlets=updated_graphlets,
            validation_reports=reports,
            structuring_issues=extra_issues,
            ready_for_hypothesis_state=ready_for_hypothesis_state,
            timings=timings,
        )
