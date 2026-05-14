from __future__ import annotations

from src.validators.evidence_atomizer import EvidenceAtomizationValidationReport


class EvidenceAtomizationPipelineError(RuntimeError):
    """Base error for failures inside the Evidence Atomizer pipeline."""

    def __init__(
        self,
        step: str,
        message: str,
        original_exception: Exception | None = None,
    ) -> None:
        self.step = step
        self.original_exception = original_exception
        detail = f"{step}: {message}"
        if original_exception is not None:
            detail = (
                f"{detail} "
                f"({type(original_exception).__name__}: {original_exception})"
            )
        super().__init__(detail)


class EvidenceAtomizationStepError(EvidenceAtomizationPipelineError):
    """Raised when a non-parse pipeline step fails."""


class EvidenceAtomizationParseError(EvidenceAtomizationStepError):
    """Raised when a pipeline step cannot parse or validate LLM JSON output."""


class EvidenceAtomizationValidationError(EvidenceAtomizationPipelineError):
    """Raised when deterministic Evidence Atomizer validation rejects output."""

    def __init__(
        self,
        step: str,
        message: str,
        validation_report: EvidenceAtomizationValidationReport,
        original_exception: Exception | None = None,
    ) -> None:
        self.validation_report = validation_report
        super().__init__(
            step=step,
            message=message,
            original_exception=original_exception,
        )
