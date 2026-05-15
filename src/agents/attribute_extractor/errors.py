from __future__ import annotations

from src.agents.attribute_extractor.result import AttributeExtractionValidationReport


class AttributeExtractionPipelineError(RuntimeError):
    """Base error for failures inside the Attribute Extractor pipeline."""

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


class AttributeExtractionStepError(AttributeExtractionPipelineError):
    """Raised when a non-parse pipeline step fails."""


class AttributeExtractionParseError(AttributeExtractionStepError):
    """Raised when a pipeline step cannot parse or validate LLM JSON output."""


class AttributeExtractionValidationError(AttributeExtractionPipelineError):
    """Raised when deterministic Attribute Extractor validation rejects output."""

    def __init__(
        self,
        step: str,
        message: str,
        validation_report: AttributeExtractionValidationReport,
        original_exception: Exception | None = None,
    ) -> None:
        self.validation_report = validation_report
        super().__init__(
            step=step,
            message=message,
            original_exception=original_exception,
        )
