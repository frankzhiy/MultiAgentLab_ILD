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

from .modules import (
    CaseStructuringAssembler,
    ClinicalSectionExtractor,
    ItemNormalizer,
    RawInputBuilder,
    SectionNormalizer,
    SourceSpanResolver,
    StageContextExtractor,
    StructuredClinicalItemExtractor,
    TemporalAmbiguityExtractor,
    TimelineAmbiguityNormalizer,
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
        self.temporal_ambiguity_extractor = TemporalAmbiguityExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.timeline_ambiguity_normalizer = TimelineAmbiguityNormalizer()
        self.source_span_resolver = SourceSpanResolver()
        self.assembler = CaseStructuringAssembler()

    def run(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringResult:
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

        items = self._run_step(
            "StructuredClinicalItemExtractor",
            lambda: self.structured_item_extractor.extract(
                raw_input,
                stage_context,
                normalized_sections.sections,
            ),
        )

        valid_section_ids = {
            section.section_id for section in normalized_sections.sections
        }
        normalized_items = self._run_step(
            "ItemNormalizer",
            lambda: self.item_normalizer.normalize(
                items,
                raw_input,
                valid_section_ids,
            ),
        )

        temporal_result = self._run_step(
            "TemporalAmbiguityExtractor",
            lambda: self.temporal_ambiguity_extractor.extract(
                raw_input,
                stage_context,
                normalized_sections.sections,
                normalized_items.items,
            ),
        )

        valid_item_ids = {item.item_id for item in normalized_items.items}
        normalized_temporal = self._run_step(
            "TimelineAmbiguityNormalizer",
            lambda: self.timeline_ambiguity_normalizer.normalize(
                timeline_events=temporal_result.timeline_events,
                ambiguities=temporal_result.ambiguities,
                raw_input=raw_input,
                valid_section_ids=valid_section_ids,
                valid_item_ids=valid_item_ids,
                section_id_map=normalized_sections.id_map,
                item_id_map=normalized_items.id_map,
            ),
        )

        resolved = self._run_step(
            "SourceSpanResolver",
            lambda: self.source_span_resolver.resolve(
                raw_input=raw_input,
                sections=normalized_sections.sections,
                items=normalized_items.items,
                timeline_events=normalized_temporal.timeline_events,
                ambiguities=normalized_temporal.ambiguities,
            ),
        )

        return self._run_step(
            "CaseStructuringAssembler",
            lambda: self.assembler.assemble(
                raw_input=raw_input,
                stage_context=stage_context,
                sections=resolved.sections,
                items=resolved.items,
                timeline_events=resolved.timeline_events,
                ambiguities=resolved.ambiguities,
            ),
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
