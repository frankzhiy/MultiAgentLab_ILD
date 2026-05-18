from __future__ import annotations

from collections.abc import Callable
from json import JSONDecodeError
from typing import TypeVar

from pydantic import ValidationError

from src.agents.case_structurer.errors import (
    CaseStructuringParseError,
    CaseStructuringPipelineError,
    CaseStructuringStepError,
)
from src.llm.chatanywhere_client import ChatAnywhereClient
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.validators.case_structurer import (
    CaseStructuringSourceSpanResult,
    validate_and_correct_item_spans,
    validate_and_correct_section_spans,
)

from .modules import (
    CaseStructuringAssembler,
    ClinicalSectionExtractor,
    ItemNormalizer,
    RawInputBuilder,
    SectionNormalizer,
    StageContextExtractor,
    StructuredClinicalItemExtractor,
)

T = TypeVar("T")


class CaseStructurerPipeline:
    """Hybrid internal pipeline for one public CaseStructurerAgent."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "case_structurer",
    ) -> None:
        self.llm_client = llm_client or ChatAnywhereClient()
        self.agent_name = agent_name

        self.raw_input_builder = RawInputBuilder()
        self.stage_context_extractor = StageContextExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.clinical_section_extractor = ClinicalSectionExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.section_normalizer = SectionNormalizer()
        self.structured_item_extractor = StructuredClinicalItemExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.item_normalizer = ItemNormalizer()
        self.assembler = CaseStructuringAssembler()

    def run(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringResult:
        return self.run_with_validation(
            raw_text=raw_text,
            case_id=case_id,
            input_order=input_order,
            parent_input_id=parent_input_id,
        ).corrected_result

    def run_with_validation(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringSourceSpanResult:
        return self._run_structuring_with_span_stages(
            raw_text=raw_text,
            case_id=case_id,
            input_order=input_order,
            parent_input_id=parent_input_id,
        )

    def _run_structuring_with_span_stages(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringSourceSpanResult:
        raw_input = self._run_step(
            "RawInputBuilder",
            lambda: self.raw_input_builder.build(
                raw_text=raw_text,
                case_id=case_id,
                input_order=input_order,
                parent_input_id=parent_input_id,
            ),
        )

        stage_context = self._run_step(
            "StageContextExtractor",
            lambda: self.stage_context_extractor.extract(raw_input),
        )

        sections = self._run_step(
            "ClinicalSectionExtractor",
            lambda: self.clinical_section_extractor.extract(
                raw_input,
                stage_context,
            ),
        )

        normalized_sections = self._run_step(
            "SectionNormalizer",
            lambda: self.section_normalizer.normalize(sections, raw_input),
        )

        section_span_result = self._run_step(
            "SectionSourceSpanValidationCorrection",
            lambda: validate_and_correct_section_spans(
                raw_text=raw_input.raw_text,
                expected_input_id=raw_input.input_id,
                sections=normalized_sections.sections,
            ),
        )
        corrected_sections = section_span_result.corrected_sections

        items = self._run_step(
            "StructuredClinicalItemExtractor",
            lambda: self.structured_item_extractor.extract(
                raw_input,
                stage_context,
                corrected_sections,
            ),
        )

        valid_section_ids = {section.section_id for section in corrected_sections}
        normalized_items = self._run_step(
            "ItemNormalizer",
            lambda: self.item_normalizer.normalize(
                items,
                raw_input,
                valid_section_ids,
            ),
        )

        item_span_result = self._run_step(
            "ItemSourceSpanValidationCorrection",
            lambda: validate_and_correct_item_spans(
                raw_text=raw_input.raw_text,
                expected_input_id=raw_input.input_id,
                sections=corrected_sections,
                items=normalized_items.items,
            ),
        )

        corrected_result = self._run_step(
            "CaseStructuringAssembler",
            lambda: self.assembler.assemble(
                raw_input=raw_input,
                stage_context=stage_context,
                sections=corrected_sections,
                items=item_span_result.corrected_items,
            ),
        )
        return CaseStructuringSourceSpanResult(
            corrected_result=corrected_result,
            section_span_result=section_span_result,
            item_span_result=item_span_result,
        )

    @staticmethod
    def _run_step(step: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except CaseStructuringPipelineError:
            raise
        except (JSONDecodeError, ValidationError) as exc:
            raise CaseStructuringParseError(
                step=step,
                message="Failed to parse or validate pipeline output.",
                original_exception=exc,
            ) from exc
        except Exception as exc:
            raise CaseStructuringStepError(
                step=step,
                message="Pipeline step failed.",
                original_exception=exc,
            ) from exc
