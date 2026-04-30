from __future__ import annotations

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem
from src.schemas.case_structurer.case_structuring_result import (
    CaseStructuringResult,
    StructuringWarning,
)
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.common import ValidationSeverity
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.stage_context import StageContext
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent


class CaseStructuringAssembler:
    """Assemble the final schema object without another LLM call."""

    def assemble(
        self,
        raw_input: RawTextInput,
        stage_context: StageContext,
        sections: list[ClinicalSection],
        items: list[StructuredClinicalItem],
        timeline_events: list[TimelineEvent],
        ambiguities: list[AmbiguityItem],
    ) -> CaseStructuringResult:
        warnings: list[StructuringWarning] = []
        ready_for_evidence_atomization = bool(sections or items)

        if not ready_for_evidence_atomization:
            warnings.append(
                StructuringWarning(
                    severity=ValidationSeverity.WARNING,
                    code="missing_clinical_structure",
                    message=(
                        "No clinical sections or structured clinical items were "
                        "produced from this input."
                    ),
                    related_object_id=raw_input.input_id,
                )
            )

        if not any([sections, items, timeline_events, ambiguities]):
            ambiguities = [
                AmbiguityItem(
                    ambiguity_id="ambiguity_001",
                    input_id=raw_input.input_id,
                    ambiguity_type="insufficient_context",
                    ambiguous_text=raw_input.raw_text,
                    possible_interpretations=[
                        "The input could not be safely structured into clinical objects."
                    ],
                    reason=(
                        "The pipeline produced no sections, items, timeline events, "
                        "or ambiguity objects."
                    ),
                    related_section_ids=[],
                    related_item_ids=[],
                    source_spans=[
                        SourceSpan(
                            span_id="span_001",
                            input_id=raw_input.input_id,
                            quoted_text=raw_input.raw_text,
                            char_start=0,
                            char_end=len(raw_input.raw_text),
                        )
                    ],
                    needs_clarification=True,
                    classification_confidence="medium",
                    notes=None,
                )
            ]

        return CaseStructuringResult(
            input=raw_input,
            stage_context=stage_context,
            clinical_sections=sections,
            structured_items=items,
            timeline_events=timeline_events,
            ambiguities=ambiguities,
            structuring_warnings=warnings,
            ready_for_evidence_atomization=ready_for_evidence_atomization,
        )
