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
    assertion_result: Any,
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

    if assertion_result is not None:
        write_json(
            output_dir / "clinical_object_assertions.json",
            obj_list(assertion_result, "clinical_object_assertions"),
        )
        write_json(
            output_dir / "clinical_assertion_warnings.json",
            obj_list(assertion_result, "assertion_warnings"),
        )

    report_html = render_html_report(
        summary=summary,
        raw_text=raw_text,
        selected_payload=selected_payload,
        case_bundle=case_bundle,
        corrected_result=corrected_result,
        assertion_result=assertion_result,
    )
    write_text(output_dir / "report.html", report_html)
