from __future__ import annotations


class CaseStructuringPipelineError(RuntimeError):
    """Base error for failures inside the Case Structurer pipeline."""

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


class CaseStructuringStepError(CaseStructuringPipelineError):
    """Raised when a non-parse pipeline step fails."""


class CaseStructuringParseError(CaseStructuringStepError):
    """Raised when a pipeline step cannot parse or validate LLM JSON output."""
