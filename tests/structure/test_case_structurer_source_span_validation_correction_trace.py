from __future__ import annotations

import json
import sys
import traceback
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.common import ValidationSeverity

try:
    from src.agents.case_structurer import CaseStructurerAgent
except ModuleNotFoundError as exc:
    CaseStructurerAgent = None  # type: ignore[assignment]
    AGENT_IMPORT_ERROR = exc
else:
    AGENT_IMPORT_ERROR = None

from src.validators.case_structurer import (
    SourceSpanCorrectionReport,
    SourceSpanValidationCorrectionResult,
    SourceSpanValidationReport,
)


VALIDATION_CORRECTION_TRACE_GUIDE: dict[str, Any] = {
    "trace_model": "case_structurer_source_span_validation_correction_trace",
    "important_note": (
        "This test uses the public CaseStructurerAgent.run_with_validation() "
        "facade, the real CaseStructurerPipeline underneath it, and real LLM "
        "outputs. No mocked LLM client or cached CaseStructuringResult fixture "
        "is used. "
        "Source-span validation and deterministic correction run after "
        "SourceSpanResolver and after initial CaseStructuringResult assembly."
    ),
    "validation_correction_effect": [
        "The initial CaseStructuringResult is not mutated in place.",
        "The corrected CaseStructuringResult is the stage output used by run().",
        "The observable bundle includes initial validation, correction actions, "
        "final validation, and residual issues.",
        "Residual ERROR issues are recorded in JSON reports and summaries, but "
        "they do not fail the unittest run.",
        "Missing runtime dependencies or missing ChatAnywhere API configuration "
        "fail the test instead of skipping it, because this is a real LLM trace.",
        "The test also records whether selected source-level clinical "
        "statements are preserved as statement-level StructuredClinicalItem "
        "objects instead of being atomized.",
        "Pipeline or assembly failures still fail the test because no final "
        "validation/correction bundle would be available to inspect.",
    ],
    "output_files_per_input": [
        {
            "file": "01_initial_case_structuring_result.json",
            "role": "Initial Case Structurer output before strict source-span validation.",
        },
        {
            "file": "02_initial_source_span_validation_report.json",
            "role": "StrictSourceSpanValidator output before correction.",
        },
        {
            "file": "03_corrected_case_structuring_result.json",
            "role": "Corrected Case Structurer output used by run().",
        },
        {
            "file": "04_source_span_correction_report.json",
            "role": "Deterministic SourceSpanCorrector action report.",
        },
        {
            "file": "05_final_source_span_validation_report.json",
            "role": "StrictSourceSpanValidator output after correction.",
        },
        {
            "file": "06_validation_correction_summary.json",
            "role": "Compact comparison of initial/final validity and correction actions.",
        },
    ],
}

STATEMENT_LEVEL_EXPECTATIONS: dict[str, list[dict[str, str]]] = {
    "01.txt": [
        {
            "code": "chief_complaint_statement_retained",
            "statement": "间断咳嗽咳痰伴胸闷气短8年",
        }
    ],
    "02.txt": [
        {
            "code": "impulse_oscillation_resistance_statement_retained",
            "statement": "气道总阻力R5、外周阻力R5-R20及近端阻力R35增高",
        }
    ],
}


class TestCaseStructurerSourceSpanValidationCorrectionTrace(unittest.TestCase):
    """Run data/*.txt through validation/correction source-span tracing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = REPO_ROOT
        cls.data_dir = cls.repo_root / "data"
        cls.input_paths = sorted(cls.data_dir.glob("*.txt"))

        if not cls.input_paths:
            raise FileNotFoundError(
                f"Missing integration-test input files under {cls.data_dir}."
            )

        if CaseStructurerAgent is None:
            raise RuntimeError(
                "Real LLM source-span validation/correction trace requires "
                "CaseStructurerAgent dependencies. Install project dependencies "
                "including openai before running this test."
            ) from AGENT_IMPORT_ERROR

        try:
            cls.agent = CaseStructurerAgent()
        except ValueError as exc:
            raise RuntimeError(
                "Real LLM source-span validation/correction trace requires "
                "CHATANYWHERE_API_KEY in the environment or .env file."
            ) from exc

    def setUp(self) -> None:
        run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.output_dir = (
            self.repo_root
            / "tests"
            / "result"
            / f"run_{run_tag}_case_structurer_source_span_validation_correction"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.written_files: list[str] = []
        self._write_json(
            "00_validation_correction_trace_guide.json",
            VALIDATION_CORRECTION_TRACE_GUIDE,
        )

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
        converter = TestCaseStructurerSourceSpanValidationCorrectionTrace._to_jsonable
        if isinstance(payload, list):
            return [converter(item) for item in payload]
        if isinstance(payload, dict):
            return {
                str(key): converter(value)
                for key, value in payload.items()
            }
        return payload

    def _write_json(
        self,
        file_name: str,
        payload: Any,
        output_dir: Path | None = None,
    ) -> Path:
        target_dir = output_dir or self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / file_name
        path.write_text(
            json.dumps(self._to_jsonable(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.written_files.append(str(path.relative_to(self.output_dir)))
        return path

    @staticmethod
    def _issue_counts_by_severity(report: SourceSpanValidationReport) -> dict[str, int]:
        counts = {severity.value: 0 for severity in ValidationSeverity}
        for issue in report.issues:
            counts[issue.severity.value] += 1
        return counts

    @staticmethod
    def _issue_counts_by_code(report: SourceSpanValidationReport) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in report.issues:
            counts[issue.code] = counts.get(issue.code, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _issue_counts_by_object_type(
        report: SourceSpanValidationReport,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in report.issues:
            counts[issue.object_type] = counts.get(issue.object_type, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _issue_examples(
        report: SourceSpanValidationReport,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return [
            issue.model_dump(mode="json")
            for issue in report.issues[:limit]
        ]

    @staticmethod
    def _residual_issue_examples(
        bundle: SourceSpanValidationCorrectionResult,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return [
            issue.model_dump(mode="json")
            for issue in bundle.residual_issues[:limit]
        ]

    @staticmethod
    def _correction_action_counts(
        report: SourceSpanCorrectionReport,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for action in report.actions:
            counts[action.code] = counts.get(action.code, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _normalize_statement_match_text(text: str) -> str:
        return "".join(text.split()).lower()

    @staticmethod
    def _item_statement_text(item: Any) -> str:
        values = [
            item.label,
            item.notes,
        ]
        return " ".join(value for value in values if value)

    @staticmethod
    def _item_source_text(item: Any) -> str:
        return " ".join(span.quoted_text for span in item.source_spans)

    @classmethod
    def _statement_level_observations(
        cls,
        input_path: Path,
        final_result: CaseStructuringResult,
    ) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []

        for expectation in STATEMENT_LEVEL_EXPECTATIONS.get(input_path.name, []):
            statement = expectation["statement"]
            normalized_statement = cls._normalize_statement_match_text(statement)
            matching_item_ids: list[str] = []
            matching_source_span_item_ids: list[str] = []

            for item in final_result.structured_items:
                item_text = cls._normalize_statement_match_text(
                    cls._item_statement_text(item)
                )
                source_text = cls._normalize_statement_match_text(
                    cls._item_source_text(item)
                )

                if normalized_statement in item_text:
                    matching_item_ids.append(item.item_id)
                if normalized_statement in source_text:
                    matching_source_span_item_ids.append(item.item_id)

            observations.append(
                {
                    "code": expectation["code"],
                    "statement": statement,
                    "statement_retained_as_item": bool(matching_item_ids),
                    "statement_present_in_source_span": bool(
                        matching_source_span_item_ids
                    ),
                    "matching_item_ids": matching_item_ids,
                    "matching_source_span_item_ids": matching_source_span_item_ids,
                }
            )

        return observations

    def _run_agent_for_input(
        self,
        input_path: Path,
        output_dir: Path,
    ) -> SourceSpanValidationCorrectionResult:
        raw_text = self._read_text_with_fallback(input_path)

        try:
            return self.agent.run_with_validation(raw_text=raw_text)
        except Exception as exc:  # noqa: BLE001
            self._write_json(
                "agent_error.json",
                {
                    "input_file": str(input_path.relative_to(self.repo_root)),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(),
                },
                output_dir=output_dir,
            )
            raise

    def _write_case_outputs(
        self,
        input_path: Path,
        bundle: SourceSpanValidationCorrectionResult,
        statement_level_observations: list[dict[str, Any]],
        output_dir: Path,
    ) -> dict[str, Any]:
        initial_result_path = self._write_json(
            "01_initial_case_structuring_result.json",
            bundle.initial_result,
            output_dir=output_dir,
        )
        initial_report_path = self._write_json(
            "02_initial_source_span_validation_report.json",
            bundle.initial_validation_report,
            output_dir=output_dir,
        )
        corrected_result_path = self._write_json(
            "03_corrected_case_structuring_result.json",
            bundle.corrected_result,
            output_dir=output_dir,
        )
        correction_report_path = self._write_json(
            "04_source_span_correction_report.json",
            bundle.correction_report,
            output_dir=output_dir,
        )
        final_report_path = self._write_json(
            "05_final_source_span_validation_report.json",
            bundle.final_validation_report,
            output_dir=output_dir,
        )
        result_unchanged = (
            bundle.initial_result.model_dump(mode="json")
            == bundle.corrected_result.model_dump(mode="json")
        )

        summary = {
            "input_file": str(input_path.relative_to(self.repo_root)),
            "initial_case_structuring_result_file": str(
                initial_result_path.relative_to(self.output_dir)
            ),
            "initial_source_span_validation_report_file": str(
                initial_report_path.relative_to(self.output_dir)
            ),
            "corrected_case_structuring_result_file": str(
                corrected_result_path.relative_to(self.output_dir)
            ),
            "source_span_correction_report_file": str(
                correction_report_path.relative_to(self.output_dir)
            ),
            "final_source_span_validation_report_file": str(
                final_report_path.relative_to(self.output_dir)
            ),
            "validation_correction_position": (
                "after SourceSpanResolver and after CaseStructuringResult assembly"
            ),
            "case_structuring_result_mutated_in_place": False,
            "case_structuring_result_changed_by_correction": not result_unchanged,
            "initial_is_valid": bundle.initial_validation_report.is_valid,
            "final_is_valid": bundle.final_validation_report.is_valid,
            "residual_issues_fail_test": False,
            "validation_correction_outcome": (
                "clean" if not bundle.residual_issues else "residual_issues"
            ),
            "initial_issue_count": len(bundle.initial_validation_report.issues),
            "final_issue_count": len(bundle.final_validation_report.issues),
            "residual_issue_count": len(bundle.residual_issues),
            "initial_issue_counts_by_severity": self._issue_counts_by_severity(
                bundle.initial_validation_report
            ),
            "final_issue_counts_by_severity": self._issue_counts_by_severity(
                bundle.final_validation_report
            ),
            "initial_issue_counts_by_code": self._issue_counts_by_code(
                bundle.initial_validation_report
            ),
            "final_issue_counts_by_code": self._issue_counts_by_code(
                bundle.final_validation_report
            ),
            "final_issue_counts_by_object_type": self._issue_counts_by_object_type(
                bundle.final_validation_report
            ),
            "initial_issue_examples": self._issue_examples(
                bundle.initial_validation_report
            ),
            "final_issue_examples": self._issue_examples(bundle.final_validation_report),
            "residual_issue_examples": self._residual_issue_examples(bundle),
            "correction_applied_count": bundle.correction_report.applied_count,
            "correction_skipped_count": bundle.correction_report.skipped_count,
            "correction_action_counts_by_code": self._correction_action_counts(
                bundle.correction_report
            ),
            "statement_level_observations": statement_level_observations,
            "case_structurer_output_counts": {
                "clinical_sections": len(bundle.corrected_result.clinical_sections),
                "structured_items": len(bundle.corrected_result.structured_items),
                "structuring_warnings": len(bundle.corrected_result.structuring_warnings),
            },
        }

        self._write_json(
            "06_validation_correction_summary.json",
            summary,
            output_dir=output_dir,
        )
        return summary

    def test_real_llm_case_structurer_output_after_source_span_validation_correction(
        self,
    ) -> None:
        summaries: list[dict[str, Any]] = []
        cases_with_residual_issues: list[dict[str, Any]] = []

        for input_path in self.input_paths:
            with self.subTest(input_file=input_path.name):
                case_output_dir = self.output_dir / input_path.stem
                bundle = self._run_agent_for_input(
                    input_path=input_path,
                    output_dir=case_output_dir,
                )

                statement_level_observations = self._statement_level_observations(
                    input_path,
                    bundle.corrected_result,
                )

                summary = self._write_case_outputs(
                    input_path=input_path,
                    bundle=bundle,
                    statement_level_observations=statement_level_observations,
                    output_dir=case_output_dir,
                )
                summaries.append(summary)

                if bundle.residual_issues:
                    cases_with_residual_issues.append(summary)

        self._write_json(
            "run_summary.json",
            {
                "trace_guide_file": "00_validation_correction_trace_guide.json",
                "trace_model": "case_structurer_source_span_validation_correction_trace",
                "data_files": [
                    str(path.relative_to(self.repo_root))
                    for path in self.input_paths
                ],
                "output_dir": str(self.output_dir.relative_to(self.repo_root)),
                "test_mode": "real_llm_trace",
                "entrypoint": "CaseStructurerAgent.run_with_validation",
                "uses_mock_llm_client": False,
                "uses_cached_case_structuring_result": False,
                "residual_issues_fail_test": False,
                "validation_correction_outcome": (
                    "clean" if not cases_with_residual_issues else "residual_issues"
                ),
                "case_count": len(summaries),
                "case_with_residual_issue_count": len(cases_with_residual_issues),
                "case_summaries": summaries,
                "written_files": self.written_files,
            },
        )

        print(
            "Case Structurer source-span validation/correction trace output: "
            f"{self.output_dir}"
        )

        self.assertTrue(
            summaries,
            "Expected at least one Case Structurer validation summary.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
