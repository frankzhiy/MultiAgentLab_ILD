from __future__ import annotations

from pydantic import TypeAdapter

from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
)
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import StageContext
from src.schemas.case_structurer.structured_clinical_item import (
    ClinicalItemType,
    StructuredClinicalItem,
)

from .base_llm_extractor import BaseLLMExtractor


class StructuredClinicalItemExtractor(BaseLLMExtractor):
    """Extract fine-grained clinical facts inside normalized sections."""

    def extract(
        self,
        raw_input: RawTextInput,
        stage_context: StageContext,
        sections: list[ClinicalSection],
    ) -> list[StructuredClinicalItem]:
        content = self.generate_json(
            prompt_path=self.prompt_path("structured_item"),
            user_payload={
                "raw_input": raw_input.model_dump(mode="json"),
                "stage_context": stage_context.model_dump(mode="json"),
                "clinical_sections": [
                    {
                        "section_id": section.section_id,
                        "section_type": section.section_type,
                        "title": section.title,
                        "normalized_text": section.normalized_text,
                        "section_order": section.section_order,
                    }
                    for section in sections
                ],
            },
            instruction=(
                "Return exactly one JSON object with key structured_items, whose "
                "value is an array of StructuredClinicalItem objects."
            ),
        )
        payload = self.parse_json_content(content)
        item_payloads = self.extract_array_payload(
            payload,
            keys=("structured_items", "items"),
        )

        valid_section_ids = [section.section_id for section in sections]
        hydrated_items = [
            self._hydrate_item_payload(raw_input, item, index, valid_section_ids)
            for index, item in enumerate(item_payloads, start=1)
        ]
        return TypeAdapter(list[StructuredClinicalItem]).validate_python(hydrated_items)

    def _hydrate_item_payload(
        self,
        raw_input: RawTextInput,
        payload: dict,
        index: int,
        valid_section_ids: list[str],
    ) -> dict:
        label = self.first_text(
            payload,
            ("label", "name", "item", "statement", "text", "quoted_text"),
        )
        if label is None:
            source_spans = payload.get("source_spans") or []
            if isinstance(source_spans, list) and source_spans:
                first_span = source_spans[0]
                if isinstance(first_span, dict):
                    label = self.first_text(
                        first_span,
                        ("quoted_text", "source_text", "text", "fragment"),
                    )

        if label is None:
            raise ValueError(
                "StructuredClinicalItem payload is missing label or an "
                "equivalent text field."
            )

        section_id = payload.get("section_id")
        if section_id not in valid_section_ids and len(valid_section_ids) == 1:
            section_id = valid_section_ids[0]

        certainty = payload.get("certainty") or "unknown"
        negation = payload.get("negation") or "unknown"
        if certainty in {
            NegationStatus.PRESENT.value,
            NegationStatus.ABSENT.value,
            NegationStatus.DENIED.value,
        }:
            if negation == "unknown":
                negation = certainty
            certainty = CertaintyLevel.DEFINITE.value

        return {
            "item_id": payload.get("item_id") or f"item_{index:03d}",
            "input_id": raw_input.input_id,
            "section_id": section_id,
            "item_type": self.coerce_enum_value(
                payload.get("item_type"),
                ClinicalItemType,
                "uncertain",
            ),
            "label": label,
            "value": payload.get("value"),
            "unit": payload.get("unit"),
            "body_site": payload.get("body_site"),
            "temporality": self.coerce_enum_value(
                payload.get("temporality"),
                TemporalRelation,
                "unknown",
            ),
            "time_text": payload.get("time_text"),
            "certainty": self.coerce_enum_value(
                certainty,
                CertaintyLevel,
                "unknown",
            ),
            "negation": self.coerce_enum_value(
                negation,
                NegationStatus,
                "unknown",
            ),
            "source_spans": self.prepare_source_spans(
                raw_input=raw_input,
                payload=payload,
                default_quoted_text=label,
                span_prefix=f"span_item_{index:03d}",
            ),
            "item_order": index,
            "classification_confidence": self.coerce_enum_value(
                payload.get("classification_confidence"),
                ConfidenceLevel,
                "medium",
            ),
            "notes": payload.get("notes"),
        }
