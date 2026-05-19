from __future__ import annotations

from pathlib import Path
from typing import Any

from phase_one_common import display_path, format_duration, obj_field, obj_list


def issue_counts(report: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in obj_list(report, "issues"):
        code = str(obj_field(issue, "code", "unknown"))
        counts[code] = counts.get(code, 0) + 1
    return dict(sorted(counts.items()))


def build_summary(
    *,
    selected_file: Path,
    repo_root: Path,
    created_at: str,
    corrected_result: Any,
    assertion_result: Any,
    durations: dict[str, float],
) -> dict[str, Any]:
    return {
        "created_at": created_at,
        "selected_file": display_path(selected_file, repo_root),
        "case_id": obj_field(obj_field(corrected_result, "input"), "case_id"),
        "input_id": obj_field(obj_field(corrected_result, "input"), "input_id"),
        "case_structuring_result_id": obj_field(corrected_result, "case_structuring_result_id"),
        "ready_for_evidence_tree_structuring": obj_field(corrected_result, "ready_for_evidence_tree_structuring"),
        "clinical_sections": len(obj_list(corrected_result, "clinical_sections")),
        "structured_items": len(obj_list(corrected_result, "structured_items")),
        "clinical_object_assertions": len(obj_list(assertion_result, "clinical_object_assertions")),
        "assertion_warnings": len(obj_list(assertion_result, "assertion_warnings")),
        "durations_seconds": durations,
        "durations_human": {key: format_duration(value) for key, value in durations.items()},
    }


def render_markdown_summary(summary: dict[str, Any]) -> str:
    duration_lines = "\n".join(
        f"- {key}: {value}" for key, value in summary["durations_human"].items()
    )
    return f"""# Phase One Test Summary

- case_id: `{summary["case_id"]}`
- input_id: `{summary["input_id"]}`
- selected_file: `{summary["selected_file"]}`
- created_at: `{summary["created_at"]}`

## Counts

- clinical_sections: {summary["clinical_sections"]}
- structured_items: {summary["structured_items"]}
- clinical_object_assertions: {summary.get("clinical_object_assertions", 0)}
- assertion_warnings: {summary.get("assertion_warnings", 0)}

## Timing

{duration_lines}

## Reader Output

Open `report.html` for the grouped, readable trace view.
"""
