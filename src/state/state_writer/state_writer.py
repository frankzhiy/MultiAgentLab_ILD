"""Unified state writer entry point."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.evidence_tree_structurer.evidence_tree_structuring_result import (
    EvidenceTreeStructuringResult,
)
from src.state.case_state import CaseState
from src.state.write_event import WriteEvent, WriteStatus
from src.validators.case_structurer import (
    CaseStructuringSourceSpanResult,
    validate_and_correct_item_spans,
    validate_and_correct_section_spans,
)


class StateWriteResult(BaseModel):
    """Result returned by a state write attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: WriteStatus
    case_id: str
    accepted: bool
    message: str
    write_event: WriteEvent
    corrected_result: Any | None = None
    source_span_result: CaseStructuringSourceSpanResult | None = None


class _StateValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    severity: ValidationSeverity
    code: str
    message: str


class StateWriter:
    """Unified entry point for deterministic writes into shared state."""

    writer_name = "state_writer"
    _case_structuring_object_type = "case_structuring_result"
    _evidence_tree_structuring_object_type = "evidence_tree_structuring_result"

    def write_case_structuring_result(
        self,
        state: CaseState,
        result: CaseStructuringResult,
        agent_name: str = "case_structurer",
    ) -> StateWriteResult:
        """Validate, correct, and write a Case Structurer result into state."""
        object_id = result.input.input_id

        if result.input.case_id != state.case_id:
            message = (
                "CaseStructuringResult rejected because result case_id does "
                "not match CaseState case_id."
            )
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._case_structuring_object_type,
                message=message,
            )

        if state.has_case_structuring_result(object_id):
            message = (
                "CaseStructuringResult rejected because this input_id already "
                "has an accepted structuring result."
            )
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._case_structuring_object_type,
                message=message,
            )

        section_span_result = validate_and_correct_section_spans(
            raw_text=result.input.raw_text,
            expected_input_id=result.input.input_id,
            sections=result.clinical_sections,
        )
        item_span_result = validate_and_correct_item_spans(
            raw_text=result.input.raw_text,
            expected_input_id=result.input.input_id,
            sections=section_span_result.corrected_sections,
            items=result.structured_items,
        )
        corrected_result = result.model_copy(
            update={
                "clinical_sections": section_span_result.corrected_sections,
                "structured_items": item_span_result.corrected_items,
            }
        )
        source_span_result = CaseStructuringSourceSpanResult(
            corrected_result=corrected_result,
            section_span_result=section_span_result,
            item_span_result=item_span_result,
        )
        section_final_report = section_span_result.final_validation_report
        item_final_report = item_span_result.final_validation_report

        if not section_final_report.is_valid or not item_final_report.is_valid:
            state.case_structuring_source_span_results.append(source_span_result)
            message = (
                "CaseStructuringResult rejected because source spans remain "
                "invalid after deterministic correction."
            )
            write_event = self._append_write_event(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._case_structuring_object_type,
                status=WriteStatus.REJECTED,
                message=message,
            )
            return StateWriteResult(
                status=WriteStatus.REJECTED,
                case_id=state.case_id,
                accepted=False,
                message=message,
                write_event=write_event,
                corrected_result=corrected_result,
                source_span_result=source_span_result,
            )

        status = (
            WriteStatus.ACCEPTED_WITH_WARNINGS
            if (
                _has_warnings(section_final_report.issues)
                or _has_warnings(item_final_report.issues)
            )
            else WriteStatus.ACCEPTED
        )
        message = (
            "CaseStructuringResult accepted with source-span validation warnings."
            if status == WriteStatus.ACCEPTED_WITH_WARNINGS
            else "CaseStructuringResult accepted."
        )

        if not state.has_input(corrected_result.input.input_id):
            state.raw_inputs.append(corrected_result.input)
        state.case_structuring_results.append(corrected_result)
        state.case_structuring_source_span_results.append(source_span_result)
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=corrected_result.input.input_id,
            object_type=self._case_structuring_object_type,
            status=status,
            message=message,
        )

        return StateWriteResult(
            status=status,
            case_id=state.case_id,
            accepted=True,
            message=message,
            write_event=write_event,
            corrected_result=corrected_result,
            source_span_result=source_span_result,
        )

    def write_evidence_tree_structuring_result(
        self,
        state: CaseState,
        result: EvidenceTreeStructuringResult,
        agent_name: str = "evidence_tree_structurer",
    ) -> StateWriteResult:
        """Validate and write an Evidence Tree Structurer result into state."""
        object_id = result.input_id

        if result.case_id != state.case_id:
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_tree_structuring_object_type,
                message=(
                    "EvidenceTreeStructuringResult rejected because result case_id "
                    "does not match CaseState case_id."
                ),
            )

        if not state.has_case_structuring_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_tree_structuring_object_type,
                message=(
                    "EvidenceTreeStructuringResult rejected because this input_id "
                    "has no accepted CaseStructuringResult."
                ),
            )

        if state.has_evidence_tree_structuring_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_tree_structuring_object_type,
                message=(
                    "EvidenceTreeStructuringResult rejected because this input_id "
                    "already has an accepted evidence tree structuring result."
                ),
            )

        validation_issues = _evidence_tree_structuring_issues(
            state=state,
            result=result,
        )
        if _has_errors(validation_issues):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_tree_structuring_object_type,
                message=(
                    "EvidenceTreeStructuringResult rejected because deterministic "
                    "validation produced error issues."
                ),
            )

        state.evidence_tree_structuring_results.append(result)
        state.evidence_trees.extend(result.evidence_trees)
        status = (
            WriteStatus.ACCEPTED_WITH_WARNINGS
            if _has_warnings(validation_issues)
            else WriteStatus.ACCEPTED
        )
        message = (
            "EvidenceTreeStructuringResult accepted with validation warnings."
            if status == WriteStatus.ACCEPTED_WITH_WARNINGS
            else "EvidenceTreeStructuringResult accepted."
        )
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=object_id,
            object_type=self._evidence_tree_structuring_object_type,
            status=status,
            message=message,
        )
        return StateWriteResult(
            status=status,
            case_id=state.case_id,
            accepted=True,
            message=message,
            write_event=write_event,
            corrected_result=result,
        )

    def _reject_without_validation(
        self,
        state: CaseState,
        agent_name: str,
        object_id: str,
        object_type: str,
        message: str,
    ) -> StateWriteResult:
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=object_id,
            object_type=object_type,
            status=WriteStatus.REJECTED,
            message=message,
        )
        return StateWriteResult(
            status=WriteStatus.REJECTED,
            case_id=state.case_id,
            accepted=False,
            message=message,
            write_event=write_event,
        )

    def _append_write_event(
        self,
        state: CaseState,
        agent_name: str,
        object_id: str | None,
        object_type: str,
        status: WriteStatus,
        message: str,
    ) -> WriteEvent:
        write_event = WriteEvent(
            case_id=state.case_id,
            writer_name=self.writer_name,
            agent_name=agent_name,
            object_type=object_type,
            object_id=object_id,
            status=status,
            message=message,
        )
        state.write_events.append(write_event)
        return write_event


def _has_warnings(issues: list[object]) -> bool:
    return any(
        getattr(issue, "severity", None) == ValidationSeverity.WARNING
        for issue in issues
    )


def _has_errors(issues: list[object]) -> bool:
    return any(
        getattr(issue, "severity", None) == ValidationSeverity.ERROR
        for issue in issues
    )


def _evidence_tree_structuring_issues(
    *,
    state: CaseState,
    result: EvidenceTreeStructuringResult,
) -> list[object]:
    source_result = _case_structuring_result_for_input(state, result.input_id)
    issues: list[object] = []
    if result.source_structuring_result_id != source_result.case_structuring_result_id:
        issues.append(
            _StateValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="source_structuring_result_id_mismatch",
                message=(
                    "EvidenceTreeStructuringResult.source_structuring_result_id "
                    "must match CaseStructuringResult.case_structuring_result_id."
                ),
            )
        )
    return issues


def _case_structuring_result_for_input(
    state: CaseState,
    input_id: str,
) -> CaseStructuringResult:
    for result in state.case_structuring_results:
        if result.input.input_id == input_id:
            return result
    raise ValueError(f"No CaseStructuringResult found for input_id={input_id!r}.")
