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


def _graphlets_by_status(structuring_result: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for graphlet in obj_list(structuring_result, "graphlets"):
        status = obj_field(graphlet, "status")
        if hasattr(status, "value"):
            key = str(status.value)
        else:
            key = str(status) if status is not None else "unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _count_relations_and_nodes(structuring_result: Any) -> tuple[int, int]:
    nodes_total = 0
    relations_total = 0
    for graphlet in obj_list(structuring_result, "graphlets"):
        nodes_total += len(obj_list(graphlet, "nodes"))
        relations_total += len(obj_list(graphlet, "relations"))
    return nodes_total, relations_total


def build_summary(
    *,
    selected_file: Path,
    repo_root: Path,
    created_at: str,
    corrected_result: Any,
    structuring_result: Any,
    durations: dict[str, float],
) -> dict[str, Any]:
    nodes_total, relations_total = _count_relations_and_nodes(structuring_result)

    frames_total = 0
    for graphlet in obj_list(structuring_result, "graphlets"):
        frames_total += len(obj_list(graphlet, "frames"))

    return {
        "created_at": created_at,
        "selected_file": display_path(selected_file, repo_root),
        "case_id": obj_field(obj_field(corrected_result, "input"), "case_id"),
        "input_id": obj_field(obj_field(corrected_result, "input"), "input_id"),
        "case_structuring_result_id": obj_field(corrected_result, "case_structuring_result_id"),
        "ready_for_evidence_graph_structuring": obj_field(
            corrected_result, "ready_for_evidence_graph_structuring"
        ),
        "clinical_sections": len(obj_list(corrected_result, "clinical_sections")),
        "structured_items": len(obj_list(corrected_result, "structured_items")),
        "clinical_object_assertions": len(
            obj_list(structuring_result, "clinical_object_assertions")
        ),
        "assertion_issues": len(obj_list(structuring_result, "assertion_issues")),
        "evidence_frames": frames_total,
        "evidence_nodes": nodes_total,
        "evidence_relations": relations_total,
        "evidence_graphlets": len(obj_list(structuring_result, "graphlets")),
        "evidence_graphlets_by_status": _graphlets_by_status(structuring_result),
        "validation_reports": len(obj_list(structuring_result, "validation_reports")),
        "structuring_issues": len(obj_list(structuring_result, "structuring_issues")),
        "ready_for_hypothesis_state": obj_field(
            structuring_result, "ready_for_hypothesis_state"
        ),
        "durations_seconds": durations,
        "durations_human": {key: format_duration(value) for key, value in durations.items()},
    }


def render_markdown_summary(summary: dict[str, Any]) -> str:
    duration_lines = "\n".join(
        f"- {key}: {value}" for key, value in summary["durations_human"].items()
    )
    graphlets_by_status = summary.get("evidence_graphlets_by_status", {}) or {}
    status_lines = "\n".join(
        f"  - {status}: {count}" for status, count in graphlets_by_status.items()
    )
    if not status_lines:
        status_lines = "  - (none)"
    return f"""# Phase One Test Summary

- case_id: `{summary["case_id"]}`
- input_id: `{summary["input_id"]}`
- selected_file: `{summary["selected_file"]}`
- created_at: `{summary["created_at"]}`

## Counts

- clinical_sections: {summary["clinical_sections"]}
- structured_items: {summary["structured_items"]}
- clinical_object_assertions: {summary.get("clinical_object_assertions", 0)}
- assertion_issues: {summary.get("assertion_issues", 0)}
- evidence_frames: {summary.get("evidence_frames", 0)}
- evidence_nodes: {summary.get("evidence_nodes", 0)}
- evidence_relations: {summary.get("evidence_relations", 0)}
- evidence_graphlets: {summary.get("evidence_graphlets", 0)}
{status_lines}
- validation_reports: {summary.get("validation_reports", 0)}
- structuring_issues: {summary.get("structuring_issues", 0)}
- ready_for_hypothesis_state: {summary.get("ready_for_hypothesis_state")}

## Timing

{duration_lines}

## Reader Output

Open `report.html` for the grouped, readable trace view.
"""
