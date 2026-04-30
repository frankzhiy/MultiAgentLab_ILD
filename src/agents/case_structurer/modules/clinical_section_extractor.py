from __future__ import annotations

from pydantic import TypeAdapter

from src.schemas.case_structurer.clinical_section import (
    ClinicalSection,
    ClinicalSectionType,
)
from src.schemas.case_structurer.common import ConfidenceLevel
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.stage_context import StageContext

from .base_llm_extractor import BaseLLMExtractor


class ClinicalSectionExtractor(BaseLLMExtractor):
    """Extract coarse clinical sections from one raw input."""

    def extract(
        self,
        raw_input: RawTextInput,
        stage_context: StageContext,
    ) -> list[ClinicalSection]:
        content = self.generate_json(
            prompt_path=self.prompt_path("clinical_section"),
            user_payload={
                "raw_input": raw_input.model_dump(mode="json"),
                "stage_context": stage_context.model_dump(mode="json"),
            },
            instruction=(
                "Return exactly one JSON object with key clinical_sections, whose "
                "value is an array of ClinicalSection objects."
            ),
        )
        payload = self.parse_json_content(content)
        section_payloads = self.extract_array_payload(
            payload,
            keys=("clinical_sections", "sections"),
        )

        hydrated_sections = [
            self._hydrate_section_payload(raw_input, section, index)
            for index, section in enumerate(section_payloads, start=1)
        ]
        return TypeAdapter(list[ClinicalSection]).validate_python(hydrated_sections)

    def _hydrate_section_payload(
        self,
        raw_input: RawTextInput,
        payload: dict,
        index: int,
    ) -> dict:
        normalized_text = self.first_text(
            payload,
            (
                "normalized_text",
                "section_text",
                "text",
                "content",
                "quoted_text",
                "summary",
            ),
        )
        if normalized_text is None:
            source_spans = payload.get("source_spans") or []
            if isinstance(source_spans, list) and source_spans:
                first_span = source_spans[0]
                if isinstance(first_span, dict):
                    normalized_text = self.first_text(
                        first_span,
                        ("quoted_text", "source_text", "text", "fragment"),
                    )

        if normalized_text is None:
            raise ValueError(
                "ClinicalSection payload is missing normalized_text or an "
                "equivalent text field."
            )

        return {
            "section_id": payload.get("section_id") or f"section_{index:03d}",
            "input_id": raw_input.input_id,
            "section_type": self.coerce_enum_value(
                payload.get("section_type"),
                ClinicalSectionType,
                "uncertain",
            ),
            "title": payload.get("title"),
            "normalized_text": normalized_text,
            "source_spans": self.prepare_source_spans(
                raw_input=raw_input,
                payload=payload,
                default_quoted_text=normalized_text,
                span_prefix=f"span_section_{index:03d}",
            ),
            "section_order": index,
            "classification_confidence": self.coerce_enum_value(
                payload.get("classification_confidence"),
                ConfidenceLevel,
                "medium",
            ),
            "parent_section_id": payload.get("parent_section_id"),
            "notes": payload.get("notes"),
        }
