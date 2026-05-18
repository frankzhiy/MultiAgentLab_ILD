from __future__ import annotations

from src.validators.evidence_tree_structurer import EvidenceTreeStructuringValidationReport


class EvidenceTreeStructuringPipelineError(RuntimeError):
    """Base error for failures inside the Evidence Tree Structurer pipeline."""

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


class EvidenceTreeStructuringStepError(EvidenceTreeStructuringPipelineError):
    """Raised when a non-parse pipeline step fails."""


class EvidenceTreeStructuringParseError(EvidenceTreeStructuringStepError):
    """Raised when a pipeline step cannot parse or validate LLM JSON output."""


class EvidenceTreeStructuringValidationError(EvidenceTreeStructuringPipelineError):
    """Raised when deterministic Evidence Tree Structurer validation rejects output."""

    def __init__(
        self,
        step: str,
        message: str,
        validation_report: EvidenceTreeStructuringValidationReport,
        original_exception: Exception | None = None,
    ) -> None:
        self.validation_report = validation_report
        super().__init__(
            step=step,
            message=message,
            original_exception=original_exception,
        )
