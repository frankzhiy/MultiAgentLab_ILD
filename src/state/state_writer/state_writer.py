"""Unified state writer entry point."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)
from src.state.case_state import CaseState
from src.state.write_event import WriteEvent, WriteStatus
from src.validators.evidence_atomizer import EvidenceAtomizationValidator
from src.validators.case_structurer import (
    SourceSpanValidationCorrectionResult,
    validate_and_correct_source_spans,
)
from src.agents.attribute_extractor.modules.attribute_extraction_validator import (
    AttributeExtractionValidator,
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
    validation_correction_result: SourceSpanValidationCorrectionResult | None = None


class StateWriter:
    """Unified entry point for deterministic writes into shared state."""

    writer_name = "state_writer"
    _case_structuring_object_type = "case_structuring_result"
    _attribute_extraction_object_type = "attribute_extraction_result"
    _evidence_atomization_object_type = "evidence_atomization_result"

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
            validation_correction_result=validation_correction_result,
        )

    def write_attribute_extraction_result(
        self,
        state: CaseState,
        result: AttributeExtractionResult,
        source_case_structuring_result: CaseStructuringResult | None = None,
        agent_name: str = "attribute_extractor",
    ) -> StateWriteResult:
        """Validate and write an Attribute Extractor result into state."""
        object_id = result.input_id

        if result.case_id != state.case_id:
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._attribute_extraction_object_type,
                message=(
                    "AttributeExtractionResult rejected because result case_id "
                    "does not match CaseState case_id."
                ),
            )

        if not state.has_case_structuring_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._attribute_extraction_object_type,
                message=(
                    "AttributeExtractionResult rejected because this input_id "
                    "has no accepted CaseStructuringResult."
                ),
            )

        if state.has_attribute_extraction_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._attribute_extraction_object_type,
                message=(
                    "AttributeExtractionResult rejected because this input_id "
                    "already has an accepted attribute extraction result."
                ),
            )

        source_result = source_case_structuring_result or _case_structuring_result_for_input(
            state,
            object_id,
        )
        validation_report = AttributeExtractionValidator().validate(
            structuring_result=source_result,
            attribute_result=result,
        )
        if not validation_report.accepted:
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._attribute_extraction_object_type,
                message=(
                    "AttributeExtractionResult rejected because deterministic "
                    "validation produced error issues."
                ),
            )

        state.attribute_extraction_results.append(result)
        state.clinical_attributes.extend(result.clinical_attributes)
        status = (
            WriteStatus.ACCEPTED_WITH_WARNINGS
            if _has_warnings(validation_report.issues)
            else WriteStatus.ACCEPTED
        )
        message = (
            "AttributeExtractionResult accepted with validation warnings."
            if status == WriteStatus.ACCEPTED_WITH_WARNINGS
            else "AttributeExtractionResult accepted."
        )
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=object_id,
            object_type=self._attribute_extraction_object_type,
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

    def write_evidence_atomization_result(
        self,
        state: CaseState,
        result: EvidenceAtomizationResult,
        source_attribute_extraction_result: AttributeExtractionResult | None = None,
        agent_name: str = "evidence_atomizer",
    ) -> StateWriteResult:
        """Validate and write an Evidence Atomizer result into state."""
        object_id = result.input_id

        if result.case_id != state.case_id:
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_atomization_object_type,
                message=(
                    "EvidenceAtomizationResult rejected because result case_id "
                    "does not match CaseState case_id."
                ),
            )

        if not state.has_attribute_extraction_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_atomization_object_type,
                message=(
                    "EvidenceAtomizationResult rejected because this input_id "
                    "has no accepted AttributeExtractionResult."
                ),
            )

        if state.has_evidence_atomization_result(object_id):
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_atomization_object_type,
                message=(
                    "EvidenceAtomizationResult rejected because this input_id "
                    "already has an accepted evidence atomization result."
                ),
            )

        source_attribute_result = (
            source_attribute_extraction_result
            or _attribute_extraction_result_for_input(state, object_id)
        )
        source_structuring_result = _case_structuring_result_for_input(state, object_id)
        validation_report = EvidenceAtomizationValidator().validate(
            structuring_result=source_structuring_result,
            attribute_result=source_attribute_result,
            atomization_result=result,
        )
        if not validation_report.accepted:
            return self._reject_without_validation(
                state=state,
                agent_name=agent_name,
                object_id=object_id,
                object_type=self._evidence_atomization_object_type,
                message=(
                    "EvidenceAtomizationResult rejected because deterministic "
                    "validation produced error issues."
                ),
            )

        state.evidence_atomization_results.append(result)
        state.evidence_atoms.extend(result.evidence_atoms)
        status = (
            WriteStatus.ACCEPTED_WITH_WARNINGS
            if _has_warnings(validation_report.issues)
            else WriteStatus.ACCEPTED
        )
        message = (
            "EvidenceAtomizationResult accepted with validation warnings."
            if status == WriteStatus.ACCEPTED_WITH_WARNINGS
            else "EvidenceAtomizationResult accepted."
        )
        write_event = self._append_write_event(
            state=state,
            agent_name=agent_name,
            object_id=object_id,
            object_type=self._evidence_atomization_object_type,
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


def _case_structuring_result_for_input(
    state: CaseState,
    input_id: str,
) -> CaseStructuringResult:
    for result in state.case_structuring_results:
        if result.input.input_id == input_id:
            return result
    raise ValueError(f"No CaseStructuringResult found for input_id={input_id!r}.")


def _attribute_extraction_result_for_input(
    state: CaseState,
    input_id: str,
) -> AttributeExtractionResult:
    for result in state.attribute_extraction_results:
        if result.input_id == input_id:
            return result
    raise ValueError(f"No AttributeExtractionResult found for input_id={input_id!r}.")
