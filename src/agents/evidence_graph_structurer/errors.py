from __future__ import annotations


class EvidenceGraphStructuringPipelineError(RuntimeError):
    """Base error for failures inside the Evidence Graph Structurer pipeline."""

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


class EvidenceGraphStructuringStepError(EvidenceGraphStructuringPipelineError):
    """Raised when a non-parse pipeline step fails."""


class EvidenceGraphStructuringParseError(EvidenceGraphStructuringStepError):
    """Raised when a pipeline step cannot parse or validate LLM JSON output."""
