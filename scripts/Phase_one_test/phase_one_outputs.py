from __future__ import annotations

from pathlib import Path
from typing import Any

from phase_one_common import obj_field, obj_list, write_json, write_text
from phase_one_report import render_html_report
from phase_one_summary import render_markdown_summary


def write_outputs(
    *,
    output_dir: Path,
    raw_text: str,
    selected_payload: dict[str, Any],
    summary: dict[str, Any],
    case_bundle: Any,
    corrected_result: Any,
    tree_structuring_bundle: Any,
    tree_structuring_result: Any,
    tree_result: Any,
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
    write_json(output_dir / "evidence_tree_structuring_result.json", tree_structuring_result)
    write_json(
        output_dir / "item_to_tree_links.json",
        obj_list(tree_structuring_result, "item_to_tree_links"),
    )
    write_json(
        output_dir / "evidence_tree_structuring_validation_report.json",
        obj_field(tree_structuring_bundle, "validation_report"),
    )
    write_json(output_dir / "evidence_trees.json", tree_result)

    assertion_resolution = obj_field(tree_structuring_bundle, "clinical_assertion_resolution")
    if assertion_resolution is not None:
        write_json(
            output_dir / "clinical_object_assertions.json",
            obj_list(assertion_resolution, "clinical_object_assertions"),
        )
        write_json(
            output_dir / "clinical_assertion_warnings.json",
            obj_list(assertion_resolution, "assertion_warnings"),
        )
    write_json(
        output_dir / "evidence_tree_structurer_timings.json",
        obj_field(tree_structuring_bundle, "pipeline_timings_seconds", {}),
    )

    report_html = render_html_report(
        summary=summary,
        raw_text=raw_text,
        selected_payload=selected_payload,
        case_bundle=case_bundle,
        corrected_result=corrected_result,
        tree_structuring_result=tree_structuring_result,
        tree_structuring_validation_report=obj_field(tree_structuring_bundle, "validation_report"),
        assertion_resolution=obj_field(tree_structuring_bundle, "clinical_assertion_resolution"),
        tree_result=tree_result,
    )
    write_text(output_dir / "report.html", report_html)
