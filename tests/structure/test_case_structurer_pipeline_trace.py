from __future__ import annotations

import json
import sys
import traceback
import unittest
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.agents.case_structurer.pipeline import CaseStructurerPipeline
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

T = TypeVar("T")

TRACE_GUIDE: dict[str, Any] = {
    "trace_model": "pipeline_stage_trace",
    "important_note": (
        "This folder is a pipeline trace, not a one-file-per-schema export. "
        "Some files show intermediate states such as extracted and normalized."
    ),
    "why_normalized_after_extracted": [
        "extracted means the first-pass clinical objects recognized from raw text.",
        "normalized means ids, order fields, input_id, and cross-object references "
        "have been made deterministic and validated for downstream use.",
        "Source spans are resolved after ids and references are stable, so every "
        "object can point back to raw text reliably.",
    ],
    "schema_inventory": [
        {
            "schema": "RawTextInput",
            "role": "Computer input wrapper: what this input is.",
            "formal_output_location": "10_case_structuring_result.json#/input",
            "trace_files": ["01_raw_input.json", "10_case_structuring_result.json"],
            "top_level_in_final_result": True,
        },
        {
            "schema": "StageContext",
            "role": (
                "Medical workflow and system-stage context: initial input, "
                "supplement, follow-up, or review."
            ),
            "formal_output_location": "10_case_structuring_result.json#/stage_context",
            "trace_files": ["02_stage_context.json", "10_case_structuring_result.json"],
            "top_level_in_final_result": True,
        },
        {
            "schema": "ClinicalSection",
            "role": "Clinical block: which large clinical sections the raw text contains.",
            "formal_output_location": "10_case_structuring_result.json#/clinical_sections",
            "trace_files": [
                "03_clinical_sections_extracted.json",
                "04_clinical_sections_normalized.json",
                "10_case_structuring_result.json",
            ],
            "top_level_in_final_result": True,
        },
        {
            "schema": "StructuredClinicalItem",
            "role": (
                "Specific clinical item inside a section, with stable ids for later "
                "reference."
            ),
            "formal_output_location": "10_case_structuring_result.json#/structured_items",
            "trace_files": [
                "05_structured_items_extracted.json",
                "06_structured_items_normalized.json",
                "10_case_structuring_result.json",
            ],
            "top_level_in_final_result": True,
        },
        {
            "schema": "TimelineEvent",
            "role": "Clinical timeline event: what happened in what order or time frame.",
            "formal_output_location": "10_case_structuring_result.json#/timeline_events",
            "trace_files": [
                "07_temporal_ambiguity_extracted.json",
                "08_temporal_ambiguity_normalized.json",
                "10_case_structuring_result.json",
            ],
            "top_level_in_final_result": True,
        },
        {
            "schema": "AmbiguityItem",
            "role": (
                "Medical uncertainty and system-safety marker: where the system must "
                "not force a hard judgment."
            ),
            "formal_output_location": "10_case_structuring_result.json#/ambiguities",
            "trace_files": [
                "07_temporal_ambiguity_extracted.json",
                "08_temporal_ambiguity_normalized.json",
                "10_case_structuring_result.json",
            ],
            "top_level_in_final_result": True,
        },
        {
            "schema": "SourceSpan",
            "role": "Raw-text provenance: where an object came from in the source text.",
            "formal_output_location": (
                "Nested under clinical_sections[], structured_items[], "
                "timeline_events[], and ambiguities[] as source_spans[]."
            ),
            "trace_files": [
                "09_source_spans_resolved.json",
                "11_source_span_index.json",
                "10_case_structuring_result.json",
            ],
            "top_level_in_final_result": False,
        },
        {
            "schema": "CaseStructuringResult",
            "role": "Computer packaging layer: the single formal output object.",
            "formal_output_location": "10_case_structuring_result.json#/",
            "trace_files": ["10_case_structuring_result.json"],
            "top_level_in_final_result": "wrapper",
        },
    ],
    "pipeline_stage_outputs": [
        {
            "file": "01_raw_input.json",
            "step": "RawInputBuilder",
            "state": "built",
            "primary_schemas": ["RawTextInput"],
        },
        {
            "file": "02_stage_context.json",
            "step": "StageContextExtractor",
            "state": "extracted_final",
            "primary_schemas": ["StageContext"],
        },
        {
            "file": "03_clinical_sections_extracted.json",
            "step": "ClinicalSectionExtractor",
            "state": "extracted",
            "primary_schemas": ["ClinicalSection"],
        },
        {
            "file": "04_clinical_sections_normalized.json",
            "step": "SectionNormalizer",
            "state": "normalized",
            "primary_schemas": ["ClinicalSection"],
        },
        {
            "file": "05_structured_items_extracted.json",
            "step": "StructuredClinicalItemExtractor",
            "state": "extracted",
            "primary_schemas": ["StructuredClinicalItem"],
        },
        {
            "file": "06_structured_items_normalized.json",
            "step": "ItemNormalizer",
            "state": "normalized",
            "primary_schemas": ["StructuredClinicalItem"],
        },
        {
            "file": "07_temporal_ambiguity_extracted.json",
            "step": "TemporalAmbiguityExtractor",
            "state": "extracted",
            "primary_schemas": ["TimelineEvent", "AmbiguityItem"],
        },
        {
            "file": "08_temporal_ambiguity_normalized.json",
            "step": "TimelineAmbiguityNormalizer",
            "state": "normalized",
            "primary_schemas": ["TimelineEvent", "AmbiguityItem"],
        },
        {
            "file": "09_source_spans_resolved.json",
            "step": "SourceSpanResolver",
            "state": "source_spans_resolved",
            "primary_schemas": [
                "ClinicalSection",
                "StructuredClinicalItem",
                "TimelineEvent",
                "AmbiguityItem",
                "SourceSpan",
            ],
        },
        {
            "file": "10_case_structuring_result.json",
            "step": "CaseStructuringAssembler",
            "state": "assembled",
            "primary_schemas": ["CaseStructuringResult"],
        },
        {
            "file": "11_source_span_index.json",
            "step": "TraceDebugExport",
            "state": "schema_oriented_debug_view",
            "primary_schemas": ["SourceSpan"],
        },
    ],
}


class TestCaseStructurerPipelineTrace(unittest.TestCase):
    """Run data/01.txt through every Case Structurer pipeline stage.

    This integration test is intended for IDE run-button usage. It writes every
    intermediate stage and the final CaseStructuringResult under tests/result/.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = REPO_ROOT
        cls.input_path = cls.repo_root / "data" / "01.txt"

        if not cls.input_path.exists():
            raise FileNotFoundError(
                "Missing input file for integration test: "
                f"{cls.input_path}. Please add data/01.txt first."
            )

        cls.raw_text = cls._read_text_with_fallback(cls.input_path)

    def setUp(self) -> None:
        run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.output_dir = (
            self.repo_root
            / "tests"
            / "result"
            / f"run_{run_tag}_case_structurer_pipeline_trace"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.written_files: list[str] = []
        self._write_json("00_trace_guide.json", TRACE_GUIDE)

    @staticmethod
    def _read_text_with_fallback(path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        raise UnicodeDecodeError(
            "unknown",
            b"",
            0,
            1,
            "Unable to decode input text with utf-8/utf-8-sig/gb18030",
        )

    @staticmethod
    def _to_jsonable(payload: Any) -> Any:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(mode="json")
        if isinstance(payload, list):
            return [TestCaseStructurerPipelineTrace._to_jsonable(item) for item in payload]
        if isinstance(payload, dict):
            return {
                str(key): TestCaseStructurerPipelineTrace._to_jsonable(value)
                for key, value in payload.items()
            }
        return payload

    def _write_json(self, file_name: str, payload: Any) -> None:
        path = self.output_dir / file_name
        path.write_text(
            json.dumps(self._to_jsonable(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.written_files.append(file_name)

    def _run_stage(
        self,
        step_name: str,
        output_file: str,
        func: Callable[[], T],
        payload_builder: Callable[[T], Any] | None = None,
    ) -> T:
        try:
            result = func()
        except Exception as exc:  # noqa: BLE001
            self._write_json(
                "pipeline_error.json",
                {
                    "failed_step": step_name,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(),
                    "input_file": str(self.input_path.relative_to(self.repo_root)),
                    "output_dir": str(self.output_dir.relative_to(self.repo_root)),
                    "written_files_before_error": self.written_files,
                },
            )
            raise

        payload = payload_builder(result) if payload_builder is not None else result
        self._write_json(output_file, payload)
        return result

    @staticmethod
    def _source_span_index(result: CaseStructuringResult) -> dict[str, Any]:
        source_spans: list[dict[str, Any]] = []

        def add_spans(
            parent_schema: str,
            parent_collection: str,
            parent_id: str,
            spans: list[Any],
        ) -> None:
            for span in spans:
                source_spans.append(
                    {
                        "parent_schema": parent_schema,
                        "parent_collection": parent_collection,
                        "parent_id": parent_id,
                        "span": span,
                    }
                )

        for section in result.clinical_sections:
            add_spans(
                "ClinicalSection",
                "clinical_sections",
                section.section_id,
                section.source_spans,
            )

        for item in result.structured_items:
            add_spans(
                "StructuredClinicalItem",
                "structured_items",
                item.item_id,
                item.source_spans,
            )

        for event in result.timeline_events:
            add_spans(
                "TimelineEvent",
                "timeline_events",
                event.event_id,
                event.source_spans,
            )

        for ambiguity in result.ambiguities:
            add_spans(
                "AmbiguityItem",
                "ambiguities",
                ambiguity.ambiguity_id,
                ambiguity.source_spans,
            )

        return {
            "note": (
                "Debug index only. The formal CaseStructuringResult keeps "
                "SourceSpan objects nested under their owning clinical objects."
            ),
            "count": len(source_spans),
            "source_spans": source_spans,
        }

    def test_run_pipeline_and_write_all_stage_outputs(self) -> None:
        pipeline = CaseStructurerPipeline()

        raw_input = self._run_stage(
            "RawInputBuilder",
            "01_raw_input.json",
            lambda: pipeline.raw_input_builder.build(raw_text=self.raw_text),
        )

        stage_context = self._run_stage(
            "StageContextExtractor",
            "02_stage_context.json",
            lambda: pipeline.stage_context_extractor.extract(raw_input),
        )

        extracted_sections = self._run_stage(
            "ClinicalSectionExtractor",
            "03_clinical_sections_extracted.json",
            lambda: pipeline.clinical_section_extractor.extract(
                raw_input,
                stage_context,
            ),
        )

        normalized_sections = self._run_stage(
            "SectionNormalizer",
            "04_clinical_sections_normalized.json",
            lambda: pipeline.section_normalizer.normalize(
                extracted_sections,
                raw_input,
            ),
            lambda result: {
                "id_map": result.id_map,
                "clinical_sections": result.sections,
            },
        )

        extracted_items = self._run_stage(
            "StructuredClinicalItemExtractor",
            "05_structured_items_extracted.json",
            lambda: pipeline.structured_item_extractor.extract(
                raw_input,
                stage_context,
                normalized_sections.sections,
            ),
        )

        valid_section_ids = {
            section.section_id for section in normalized_sections.sections
        }
        normalized_items = self._run_stage(
            "ItemNormalizer",
            "06_structured_items_normalized.json",
            lambda: pipeline.item_normalizer.normalize(
                extracted_items,
                raw_input,
                valid_section_ids,
            ),
            lambda result: {
                "id_map": result.id_map,
                "structured_items": result.items,
            },
        )

        temporal_result = self._run_stage(
            "TemporalAmbiguityExtractor",
            "07_temporal_ambiguity_extracted.json",
            lambda: pipeline.temporal_ambiguity_extractor.extract(
                raw_input,
                stage_context,
                normalized_sections.sections,
                normalized_items.items,
            ),
        )

        valid_item_ids = {item.item_id for item in normalized_items.items}
        normalized_temporal = self._run_stage(
            "TimelineAmbiguityNormalizer",
            "08_temporal_ambiguity_normalized.json",
            lambda: pipeline.timeline_ambiguity_normalizer.normalize(
                timeline_events=temporal_result.timeline_events,
                ambiguities=temporal_result.ambiguities,
                raw_input=raw_input,
                valid_section_ids=valid_section_ids,
                valid_item_ids=valid_item_ids,
                section_id_map=normalized_sections.id_map,
                item_id_map=normalized_items.id_map,
            ),
            lambda result: {
                "event_id_map": result.event_id_map,
                "ambiguity_id_map": result.ambiguity_id_map,
                "timeline_events": result.timeline_events,
                "ambiguities": result.ambiguities,
            },
        )

        resolved = self._run_stage(
            "SourceSpanResolver",
            "09_source_spans_resolved.json",
            lambda: pipeline.source_span_resolver.resolve(
                raw_input=raw_input,
                sections=normalized_sections.sections,
                items=normalized_items.items,
                timeline_events=normalized_temporal.timeline_events,
                ambiguities=normalized_temporal.ambiguities,
            ),
            lambda result: {
                "clinical_sections": result.sections,
                "structured_items": result.items,
                "timeline_events": result.timeline_events,
                "ambiguities": result.ambiguities,
            },
        )

        final_result = self._run_stage(
            "CaseStructuringAssembler",
            "10_case_structuring_result.json",
            lambda: pipeline.assembler.assemble(
                raw_input=raw_input,
                stage_context=stage_context,
                sections=resolved.sections,
                items=resolved.items,
                timeline_events=resolved.timeline_events,
                ambiguities=resolved.ambiguities,
            ),
        )

        source_span_index = self._source_span_index(final_result)
        self._write_json(
            "11_source_span_index.json",
            source_span_index,
        )

        self._write_json(
            "run_summary.json",
            {
                "trace_guide_file": "00_trace_guide.json",
                "trace_model": "pipeline_stage_trace",
                "input_file": str(self.input_path.relative_to(self.repo_root)),
                "output_dir": str(self.output_dir.relative_to(self.repo_root)),
                "case_id": final_result.input.case_id,
                "input_id": final_result.input.input_id,
                "counts": {
                    "clinical_sections": len(final_result.clinical_sections),
                    "structured_items": len(final_result.structured_items),
                    "timeline_events": len(final_result.timeline_events),
                    "ambiguities": len(final_result.ambiguities),
                    "source_spans": source_span_index["count"],
                    "structuring_warnings": len(final_result.structuring_warnings),
                },
                "ready_for_evidence_atomization": (
                    final_result.ready_for_evidence_atomization
                ),
                "written_files": self.written_files,
            },
        )

        print(f"Case Structurer trace output: {self.output_dir}")
        self.assertIsInstance(final_result, CaseStructuringResult)
        for file_name in self.written_files:
            self.assertTrue(
                (self.output_dir / file_name).exists(),
                f"Missing output file: {file_name}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
