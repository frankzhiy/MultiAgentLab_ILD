from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.agents.case_structurer import CaseStructurerAgent


class TestCaseStructurerE2E(unittest.TestCase):
    """End-to-end integration test for free-text to CaseStructuringResult."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.input_path = cls.repo_root / "data" / "01.txt"

        if not cls.input_path.exists():
            raise FileNotFoundError(
                "Missing input file for integration test: "
                f"{cls.input_path}. Please add data/01.txt first."
            )

        cls.raw_text = cls._read_text_with_fallback(cls.input_path)
        cls.agent = CaseStructurerAgent()

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
    def _write_json(path: Path, payload: object) -> None:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def test_free_text_to_case_structuring_result(self) -> None:
        result = self.agent.run(raw_text=self.raw_text)

        run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = self.repo_root / "tests" / "result" / f"run_{run_tag}_{result.input.case_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        payloads: dict[str, object] = {
            "raw_text_input.json": result.input.model_dump(mode="json"),
            "stage_context.json": result.stage_context.model_dump(mode="json"),
            "clinical_sections.json": [
                section.model_dump(mode="json") for section in result.clinical_sections
            ],
            "structured_items.json": [
                item.model_dump(mode="json") for item in result.structured_items
            ],
            "timeline_events.json": [
                event.model_dump(mode="json") for event in result.timeline_events
            ],
            "ambiguities.json": [
                ambiguity.model_dump(mode="json") for ambiguity in result.ambiguities
            ],
            "structuring_warnings.json": [
                warning.model_dump(mode="json") for warning in result.structuring_warnings
            ],
            "case_structuring_result.json": result.model_dump(mode="json"),
        }

        for file_name, payload in payloads.items():
            self._write_json(output_dir / file_name, payload)

        run_summary = {
            "run_tag": run_tag,
            "output_dir": str(output_dir.relative_to(self.repo_root)),
            "input_file": str(self.input_path.relative_to(self.repo_root)),
            "case_id": result.input.case_id,
            "input_id": result.input.input_id,
            "counts": {
                "clinical_sections": len(result.clinical_sections),
                "structured_items": len(result.structured_items),
                "timeline_events": len(result.timeline_events),
                "ambiguities": len(result.ambiguities),
                "structuring_warnings": len(result.structuring_warnings),
            },
            "ready_for_evidence_atomization": result.ready_for_evidence_atomization,
        }
        self._write_json(output_dir / "run_summary.json", run_summary)

        for file_name in payloads:
            self.assertTrue((output_dir / file_name).exists(), f"Missing output file: {file_name}")


if __name__ == "__main__":
    unittest.main()
