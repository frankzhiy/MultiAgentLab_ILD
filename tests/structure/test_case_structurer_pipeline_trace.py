# from __future__ import annotations

# import json
# import sys
# import traceback
# import unittest
# from collections.abc import Callable
# from datetime import datetime, timezone
# from pathlib import Path
# from typing import Any, TypeVar

# REPO_ROOT = Path(__file__).resolve().parents[2]
# if str(REPO_ROOT) not in sys.path:
#     sys.path.insert(0, str(REPO_ROOT))

# from src.agents.case_structurer.pipeline import CaseStructurerPipeline
# from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
# from src.validators.case_structurer import (
#     validate_and_correct_item_spans,
#     validate_and_correct_section_spans,
# )

# T = TypeVar("T")

# TRACE_GUIDE: dict[str, Any] = {
#     "trace_model": "pipeline_stage_trace",
#     "important_note": (
#         "This folder is a pipeline trace, not a one-file-per-schema export. "
#         "Some files show intermediate states such as extracted and normalized. "
#         "The assembled result is then passed through source-span validation and "
#         "deterministic correction; public run() returns the corrected result."
#     ),
#     "why_normalized_after_extracted": [
#         "extracted means the first-pass clinical objects recognized from raw text.",
#         "normalized means ids, order fields, input_id, and cross-object references "
#         "have been made deterministic and validated for downstream use.",
#         "Source spans are resolved after ids and references are stable, so every "
#         "object can point back to raw text reliably.",
#     ],
#     "schema_inventory": [
#         {
#             "schema": "RawTextInput",
#             "role": "Computer input wrapper: what this input is.",
#             "formal_output_location": "08_case_structuring_result.json#/input",
#             "trace_files": ["01_raw_input.json", "08_case_structuring_result.json"],
#             "top_level_in_final_result": True,
#         },
#         {
#             "schema": "StageContext",
#             "role": (
#                 "Medical workflow and system-stage context: initial input, "
#                 "supplement, follow-up, or review."
#             ),
#             "formal_output_location": "08_case_structuring_result.json#/stage_context",
#             "trace_files": ["02_stage_context.json", "08_case_structuring_result.json"],
#             "top_level_in_final_result": True,
#         },
#         {
#             "schema": "ClinicalSection",
#             "role": "Clinical block: which large clinical sections the raw text contains.",
#             "formal_output_location": "08_case_structuring_result.json#/clinical_sections",
#             "trace_files": [
#                 "03_clinical_sections_extracted.json",
#                 "04_clinical_sections_normalized.json",
#                 "08_case_structuring_result.json",
#             ],
#             "top_level_in_final_result": True,
#         },
#         {
#             "schema": "StructuredClinicalItem",
#             "role": (
#                 "Source-level clinical statement inside a section, with stable ids "
#                 "for downstream evidence atomization."
#             ),
#             "formal_output_location": "08_case_structuring_result.json#/structured_items",
#             "trace_files": [
#                 "05_structured_items_extracted.json",
#                 "06_structured_items_normalized.json",
#                 "08_case_structuring_result.json",
#             ],
#             "top_level_in_final_result": True,
#         },
#         {
#             "schema": "SourceSpan",
#             "role": "Raw-text provenance: where an object came from in the source text.",
#             "formal_output_location": (
#                 "Nested under clinical_sections[] and structured_items[] as "
#                 "source_spans[] in 09_case_structuring_result.json."
#             ),
#             "trace_files": [
#                 "05_section_source_span_validation_correction.json",
#                 "08_item_source_span_validation_correction.json",
#                 "09_case_structuring_result.json",
#                 "10_source_span_index.json",
#             ],
#             "top_level_in_final_result": False,
#         },
#         {
#             "schema": "CaseStructuringResult",
#             "role": "Computer packaging layer: the single formal output object.",
#             "formal_output_location": "09_case_structuring_result.json",
#             "trace_files": [
#                 "09_case_structuring_result.json",
#             ],
#             "top_level_in_final_result": "wrapper",
#         },
#     ],
#     "pipeline_stage_outputs": [
#         {
#             "file": "01_raw_input.json",
#             "step": "RawInputBuilder",
#             "state": "built",
#             "primary_schemas": ["RawTextInput"],
#         },
#         {
#             "file": "02_stage_context.json",
#             "step": "StageContextExtractor",
#             "state": "extracted_final",
#             "primary_schemas": ["StageContext"],
#         },
#         {
#             "file": "03_clinical_sections_extracted.json",
#             "step": "ClinicalSectionExtractor",
#             "state": "extracted",
#             "primary_schemas": ["ClinicalSection"],
#         },
#         {
#             "file": "04_clinical_sections_normalized.json",
#             "step": "SectionNormalizer",
#             "state": "normalized",
#             "primary_schemas": ["ClinicalSection"],
#         },
#         {
#             "file": "05_section_source_span_validation_correction.json",
#             "step": "SectionSourceSpanValidationCorrection",
#             "state": "validated_and_corrected",
#             "primary_schemas": [
#                 "ClinicalSection",
#                 "SourceSpanValidationReport",
#                 "SourceSpanCorrectionReport",
#             ],
#         },
#         {
#             "file": "06_structured_items_extracted.json",
#             "step": "StructuredClinicalItemExtractor",
#             "state": "extracted",
#             "primary_schemas": ["StructuredClinicalItem"],
#         },
#         {
#             "file": "07_structured_items_normalized.json",
#             "step": "ItemNormalizer",
#             "state": "normalized",
#             "primary_schemas": ["StructuredClinicalItem"],
#         },
#         {
#             "file": "08_item_source_span_validation_correction.json",
#             "step": "ItemSourceSpanValidationCorrection",
#             "state": "validated_and_corrected",
#             "primary_schemas": [
#                 "StructuredClinicalItem",
#                 "SourceSpanValidationReport",
#                 "SourceSpanCorrectionReport",
#             ],
#         },
#         {
#             "file": "09_case_structuring_result.json",
#             "step": "CaseStructuringAssembler",
#             "state": "assembled",
#             "primary_schemas": ["CaseStructuringResult"],
#         },
#         {
#             "file": "10_source_span_index.json",
#             "step": "TraceDebugExport",
#             "state": "schema_oriented_debug_view",
#             "primary_schemas": ["SourceSpan"],
#         },
#     ],
# }


# class TestCaseStructurerPipelineTrace(unittest.TestCase):
#     """Run data/01.txt through every Case Structurer pipeline stage.

#     This integration test is intended for IDE run-button usage. It writes every
#     intermediate stage and the final CaseStructuringResult under tests/result/.
#     """

#     @classmethod
#     def setUpClass(cls) -> None:
#         cls.repo_root = REPO_ROOT
#         cls.input_path = cls.repo_root / "data" / "01.txt"

#         if not cls.input_path.exists():
#             raise FileNotFoundError(
#                 "Missing input file for integration test: "
#                 f"{cls.input_path}. Please add data/01.txt first."
#             )

#         cls.raw_text = cls._read_text_with_fallback(cls.input_path)

#     def setUp(self) -> None:
#         run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
#         self.output_dir = (
#             self.repo_root
#             / "tests"
#             / "result"
#             / f"run_{run_tag}_case_structurer_pipeline_trace"
#         )
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#         self.written_files: list[str] = []
#         self._write_json("00_trace_guide.json", TRACE_GUIDE)

#     @staticmethod
#     def _read_text_with_fallback(path: Path) -> str:
#         for encoding in ("utf-8", "utf-8-sig", "gb18030"):
#             try:
#                 return path.read_text(encoding=encoding)
#             except UnicodeDecodeError:
#                 continue

#         raise UnicodeDecodeError(
#             "unknown",
#             b"",
#             0,
#             1,
#             "Unable to decode input text with utf-8/utf-8-sig/gb18030",
#         )

#     @staticmethod
#     def _to_jsonable(payload: Any) -> Any:
#         if hasattr(payload, "model_dump"):
#             return payload.model_dump(mode="json")
#         if isinstance(payload, list):
#             return [TestCaseStructurerPipelineTrace._to_jsonable(item) for item in payload]
#         if isinstance(payload, dict):
#             return {
#                 str(key): TestCaseStructurerPipelineTrace._to_jsonable(value)
#                 for key, value in payload.items()
#             }
#         return payload

#     def _write_json(self, file_name: str, payload: Any) -> None:
#         path = self.output_dir / file_name
#         path.write_text(
#             json.dumps(self._to_jsonable(payload), ensure_ascii=False, indent=2),
#             encoding="utf-8",
#         )
#         self.written_files.append(file_name)

#     def _run_stage(
#         self,
#         step_name: str,
#         output_file: str,
#         func: Callable[[], T],
#         payload_builder: Callable[[T], Any] | None = None,
#     ) -> T:
#         try:
#             result = func()
#         except Exception as exc:  # noqa: BLE001
#             self._write_json(
#                 "pipeline_error.json",
#                 {
#                     "failed_step": step_name,
#                     "error_type": type(exc).__name__,
#                     "error_message": str(exc),
#                     "traceback": traceback.format_exc(),
#                     "input_file": str(self.input_path.relative_to(self.repo_root)),
#                     "output_dir": str(self.output_dir.relative_to(self.repo_root)),
#                     "written_files_before_error": self.written_files,
#                 },
#             )
#             raise

#         payload = payload_builder(result) if payload_builder is not None else result
#         self._write_json(output_file, payload)
#         return result

#     @staticmethod
#     def _source_span_index(result: CaseStructuringResult) -> dict[str, Any]:
#         source_spans: list[dict[str, Any]] = []

#         def add_spans(
#             parent_schema: str,
#             parent_collection: str,
#             parent_id: str,
#             spans: list[Any],
#         ) -> None:
#             for span in spans:
#                 source_spans.append(
#                     {
#                         "parent_schema": parent_schema,
#                         "parent_collection": parent_collection,
#                         "parent_id": parent_id,
#                         "span": span,
#                     }
#                 )

#         for section in result.clinical_sections:
#             add_spans(
#                 "ClinicalSection",
#                 "clinical_sections",
#                 section.section_id,
#                 section.source_spans,
#             )

#         for item in result.structured_items:
#             add_spans(
#                 "StructuredClinicalItem",
#                 "structured_items",
#                 item.item_id,
#                 item.source_spans,
#             )

#         return {
#             "note": (
#                 "Debug index only. The formal CaseStructuringResult keeps "
#                 "SourceSpan objects nested under their owning clinical objects."
#             ),
#             "count": len(source_spans),
#             "source_spans": source_spans,
#         }

#     def test_run_pipeline_and_write_all_stage_outputs(self) -> None:
#         pipeline = CaseStructurerPipeline()

#         raw_input = self._run_stage(
#             "RawInputBuilder",
#             "01_raw_input.json",
#             lambda: pipeline.raw_input_builder.build(raw_text=self.raw_text),
#         )

#         stage_context = self._run_stage(
#             "StageContextExtractor",
#             "02_stage_context.json",
#             lambda: pipeline.stage_context_extractor.extract(raw_input),
#         )

#         extracted_sections = self._run_stage(
#             "ClinicalSectionExtractor",
#             "03_clinical_sections_extracted.json",
#             lambda: pipeline.clinical_section_extractor.extract(
#                 raw_input,
#                 stage_context,
#             ),
#         )

#         normalized_sections = self._run_stage(
#             "SectionNormalizer",
#             "04_clinical_sections_normalized.json",
#             lambda: pipeline.section_normalizer.normalize(
#                 extracted_sections,
#                 raw_input,
#             ),
#             lambda result: {
#                 "id_map": result.id_map,
#                 "clinical_sections": result.sections,
#             },
#         )

#         section_span_result = self._run_stage(
#             "SectionSourceSpanValidationCorrection",
#             "05_section_source_span_validation_correction.json",
#             lambda: validate_and_correct_section_spans(
#                 raw_text=raw_input.raw_text,
#                 expected_input_id=raw_input.input_id,
#                 sections=normalized_sections.sections,
#             ),
#         )
#         corrected_sections = section_span_result.corrected_sections

#         extracted_items = self._run_stage(
#             "StructuredClinicalItemExtractor",
#             "06_structured_items_extracted.json",
#             lambda: pipeline.structured_item_extractor.extract(
#                 raw_input,
#                 stage_context,
#                 corrected_sections,
#             ),
#         )

#         valid_section_ids = {section.section_id for section in corrected_sections}
#         normalized_items = self._run_stage(
#             "ItemNormalizer",
#             "07_structured_items_normalized.json",
#             lambda: pipeline.item_normalizer.normalize(
#                 extracted_items,
#                 raw_input,
#                 valid_section_ids,
#             ),
#             lambda result: {
#                 "id_map": result.id_map,
#                 "structured_items": result.items,
#             },
#         )

#         item_span_result = self._run_stage(
#             "ItemSourceSpanValidationCorrection",
#             "08_item_source_span_validation_correction.json",
#             lambda: validate_and_correct_item_spans(
#                 raw_text=raw_input.raw_text,
#                 expected_input_id=raw_input.input_id,
#                 sections=corrected_sections,
#                 items=normalized_items.items,
#             ),
#         )

#         final_result = self._run_stage(
#             "CaseStructuringAssembler",
#             "09_case_structuring_result.json",
#             lambda: pipeline.assembler.assemble(
#                 raw_input=raw_input,
#                 stage_context=stage_context,
#                 sections=corrected_sections,
#                 items=item_span_result.corrected_items,
#             ),
#         )
#         source_span_index = self._source_span_index(final_result)
#         self._write_json("10_source_span_index.json", source_span_index)

#         corrected_result = final_result.model_copy(
#             update={
#                 "clinical_sections": corrected_sections,
#                 "structured_items": item_span_result.corrected_items,
#             }
#         )
#         corrected_source_span_index = self._source_span_index(corrected_result)

#         self._write_json(
#             "run_summary.json",
#             {
#                 "trace_guide_file": "00_trace_guide.json",
#                 "trace_model": "pipeline_stage_trace",
#                 "input_file": str(self.input_path.relative_to(self.repo_root)),
#                 "output_dir": str(self.output_dir.relative_to(self.repo_root)),
#                 "case_id": corrected_result.input.case_id,
#                 "input_id": corrected_result.input.input_id,
#                 "section_source_span_validation_is_valid": (
#                     section_span_result.final_validation_report.is_valid
#                 ),
#                 "item_source_span_validation_is_valid": (
#                     item_span_result.final_validation_report.is_valid
#                 ),
#                 "section_correction_applied_count": (
#                     section_span_result.correction_report.applied_count
#                 ),
#                 "section_correction_skipped_count": (
#                     section_span_result.correction_report.skipped_count
#                 ),
#                 "item_correction_applied_count": (
#                     item_span_result.correction_report.applied_count
#                 ),
#                 "item_correction_skipped_count": (
#                     item_span_result.correction_report.skipped_count
#                 ),
#                 "counts": {
#                     "clinical_sections": len(corrected_result.clinical_sections),
#                     "structured_items": len(corrected_result.structured_items),
#                     "source_spans_after_stage_correction": source_span_index["count"],
#                     "source_spans_after_correction": corrected_source_span_index[
#                         "count"
#                     ],
#                     "structuring_warnings": len(corrected_result.structuring_warnings),
#                 },
#                 "ready_for_evidence_atomization": (
#                     corrected_result.ready_for_evidence_atomization
#                 ),
#                 "written_files": self.written_files,
#             },
#         )

#         print(f"Case Structurer trace output: {self.output_dir}")
#         self.assertIsInstance(corrected_result, CaseStructuringResult)
#         for file_name in self.written_files:
#             self.assertTrue(
#                 (self.output_dir / file_name).exists(),
#                 f"Missing output file: {file_name}",
#             )


# if __name__ == "__main__":
#     unittest.main(verbosity=2)
