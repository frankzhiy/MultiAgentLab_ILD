"""Unified state writer entry point."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.common import ValidationSeverity
from src.state.case_state import CaseState
from src.state.write_event import WriteEvent, WriteStatus
from src.validators.case_structurer import (
    SourceSpanValidationCorrectionResult,
    validate_and_correct_source_spans,
)


class StateWriteResult(BaseModel):
    """Result returned by a state write attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: WriteStatus
    case_id: str
    accepted: bool
    message: str
    write_event: WriteEvent
    corrected_result: CaseStructuringResult | None = None
    validation_correction_result: SourceSpanValidationCorrectionResult | None = None


class StateWriter:
    """Unified entry point for deterministic writes into shared state."""

    writer_name = "state_writer"
    _case_structuring_object_type = "case_structuring_result"

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
                message=message,
            )

        validation_correction_result = validate_and_correct_source_spans(result)
        corrected_result = validation_correction_result.corrected_result
        final_report = validation_correction_result.final_validation_report

        if not final_report.is_valid:
            state.source_span_validation_correction_results.append(
                validation_correction_result
            )
            message = (
                "CaseStructuringResult rejected because source spans remain "
                "invalid after deterministic correction."
            )
            write_event = self._append_write_event(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
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
                validation_correction_result=validation_correction_result,
            )

        status = (
            WriteStatus.ACCEPTED_WITH_WARNINGS
            if _has_warnings(final_report.issues)
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
        state.source_span_validation_correction_results.append(
            validation_correction_result
        )
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=corrected_result.input.input_id,
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
            validation_correction_result=validation_correction_result,
        )

    def _reject_without_validation(
        self,
        state: CaseState,
        agent_name: str,
        object_id: str,
        message: str,
    ) -> StateWriteResult:
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=object_id,
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
        status: WriteStatus,
        message: str,
    ) -> WriteEvent:
        write_event = WriteEvent(
            case_id=state.case_id,
            writer_name=self.writer_name,
            agent_name=agent_name,
            object_type=self._case_structuring_object_type,
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
