from __future__ import annotations

from pathlib import Path
from typing import Any

from phase_one_common import obj_field, obj_list, write_json, write_text
from phase_one_report import render_html_report
from phase_one_summary import render_markdown_summary


def _collect_frames(structuring_result: Any) -> list[Any]:
    frames: list[Any] = []
    for graphlet in obj_list(structuring_result, "graphlets"):
        frames.extend(obj_list(graphlet, "frames"))
    return frames


def _collect_nodes(structuring_result: Any) -> list[Any]:
    nodes: list[Any] = []
    for graphlet in obj_list(structuring_result, "graphlets"):
        nodes.extend(obj_list(graphlet, "nodes"))
    return nodes


def _collect_relations(structuring_result: Any) -> list[Any]:
    relations: list[Any] = []
    for graphlet in obj_list(structuring_result, "graphlets"):
        relations.extend(obj_list(graphlet, "relations"))
    return relations


def write_outputs(
    *,
    output_dir: Path,
    raw_text: str,
    selected_payload: dict[str, Any],
    summary: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    structuring_result: Any,
) -> None:
    write_text(output_dir / "raw_input.txt", raw_text)
    write_json(output_dir / "selected_file.json", selected_payload)
    write_json(output_dir / "summary.json", summary)
    write_text(output_dir / "summary.md", render_markdown_summary(summary))
    write_json(output_dir / "case_structuring_result.json", corrected_result)
    write_json(
        output_dir / "section_source_span_validation_correction.json",
        obj_field(case_bundle, "section_span_result"),
    )
    write_json(
        output_dir / "item_source_span_validation_correction.json",
        obj_field(case_bundle, "item_span_result"),
    )

    if structuring_result is not None:
        write_json(
            output_dir / "evidence_structuring_result.json",
            structuring_result,
        )
        write_json(
            output_dir / "clinical_object_assertions.json",
            obj_list(structuring_result, "clinical_object_assertions"),
        )
        write_json(
            output_dir / "assertion_issues.json",
            obj_list(structuring_result, "assertion_issues"),
        )
        write_json(
            output_dir / "evidence_frames.json",
            _collect_frames(structuring_result),
        )
        write_json(
            output_dir / "evidence_nodes.json",
            _collect_nodes(structuring_result),
        )
        write_json(
            output_dir / "evidence_relations.json",
            _collect_relations(structuring_result),
        )
        write_json(
            output_dir / "evidence_graphlets.json",
            obj_list(structuring_result, "graphlets"),
        )
        write_json(
            output_dir / "evidence_graph_validation_reports.json",
            obj_list(structuring_result, "validation_reports"),
        )
        write_json(
            output_dir / "structuring_issues.json",
            obj_list(structuring_result, "structuring_issues"),
        )

    report_html = render_html_report(
        summary=summary,
        raw_text=raw_text,
        selected_payload=selected_payload,
        case_bundle=case_bundle,
        corrected_result=corrected_result,
        structuring_result=structuring_result,
    )
    write_text(output_dir / "report.html", report_html)
