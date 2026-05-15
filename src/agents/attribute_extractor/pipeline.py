from __future__ import annotations

from collections.abc import Callable
from json import JSONDecodeError
from typing import TYPE_CHECKING, TypeVar

from pydantic import ValidationError

from src.agents.attribute_extractor.errors import (
    AttributeExtractionParseError,
    AttributeExtractionPipelineError,
    AttributeExtractionStepError,
    AttributeExtractionValidationError,
)
from src.agents.attribute_extractor.result import AttributeExtractionValidationResult
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
    AttributeExtractionWarning,
)
from src.schemas.attribute_extractor.common import ValidationSeverity
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

from .modules import (
    AttributeAssembler,
    AttributeExtractionValidator,
    AttributeNormalizer,
    AttributeSpanRoleExtractor,
    AttributeSpanValidator,
    RoleConstraintValidator,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient

T = TypeVar("T")


class AttributeExtractorPipeline:
    """Hybrid internal pipeline for one public AttributeExtractorAgent."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "attribute_extractor",
    ) -> None:
        if llm_client is None:
            from src.llm.chatanywhere_client import ChatAnywhereClient

            llm_client = ChatAnywhereClient()

        self.llm_client = llm_client
        self.agent_name = agent_name
        self.attribute_span_role_extractor = AttributeSpanRoleExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.attribute_span_validator = AttributeSpanValidator()
        self.role_constraint_validator = RoleConstraintValidator()
        self.attribute_normalizer = AttributeNormalizer()
        self.attribute_assembler = AttributeAssembler()
        self.validator = AttributeExtractionValidator()

    def run(
        self,
        structuring_result: CaseStructuringResult,
    ) -> AttributeExtractionResult:
        validation_result = self.run_with_validation(structuring_result)
        if not validation_result.validation_report.accepted:
            raise AttributeExtractionValidationError(
                step="AttributeExtractionValidator",
                message="Attribute Extractor validation rejected the result.",
                validation_report=validation_result.validation_report,
            )
        return validation_result.attribute_extraction_result

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
    ) -> AttributeExtractionValidationResult:
        if not structuring_result.ready_for_attribute_extraction:
            attribute_result = self._run_step(
                "GuardedAttributeExtractionResult",
                lambda: AttributeExtractionResult(
                    case_id=structuring_result.input.case_id,
                    input_id=structuring_result.input.input_id,
                    source_structuring_result_id=(
                        structuring_result.case_structuring_result_id
                    ),
                    clinical_attributes=[],
                    extraction_warnings=[
                        AttributeExtractionWarning(
                            severity=ValidationSeverity.ERROR,
                            code="structuring_result_not_ready",
                            message=(
                                "Case structuring result is not ready for "
                                "attribute extraction."
                            ),
                        )
                    ],
                    ready_for_evidence_atomization=False,
                ),
            )
            validation_report = self._run_step(
                "AttributeExtractionValidator",
                lambda: self.validator.validate(
                    structuring_result=structuring_result,
                    attribute_result=attribute_result,
                ),
            )
            return AttributeExtractionValidationResult(
                attribute_extraction_result=attribute_result,
                validation_report=validation_report,
            )

        draft_payload = self._run_step(
            "AttributeSpanRoleExtractor",
            lambda: self.attribute_span_role_extractor.extract(structuring_result),
        )
        span_validated = self._run_step(
            "AttributeSpanValidator",
            lambda: self.attribute_span_validator.validate(
                structuring_result,
                draft_payload,
            ),
        )
        role_validated = self._run_step(
            "RoleConstraintValidator",
            lambda: self.role_constraint_validator.validate(
                structuring_result,
                span_validated,
            ),
        )
        normalized = self._run_step(
            "AttributeNormalizer",
            lambda: self.attribute_normalizer.normalize(role_validated),
        )
        attribute_result = self._run_step(
            "AttributeAssembler",
            lambda: self.attribute_assembler.assemble(
                structuring_result,
                normalized,
            ),
        )
        validation_report = self._run_step(
            "AttributeExtractionValidator",
            lambda: self.validator.validate(
                structuring_result=structuring_result,
                attribute_result=attribute_result,
            ),
        )
        return AttributeExtractionValidationResult(
            attribute_extraction_result=attribute_result,
            validation_report=validation_report,
        )

    @staticmethod
    def _run_step(step: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except AttributeExtractionPipelineError:
            raise
        except (JSONDecodeError, ValidationError) as exc:
            raise AttributeExtractionParseError(
                step=step,
                message="Failed to parse or validate pipeline output.",
                original_exception=exc,
            ) from exc
        except Exception as exc:
            raise AttributeExtractionStepError(
                step=step,
                message="Pipeline step failed.",
                original_exception=exc,
            ) from exc
