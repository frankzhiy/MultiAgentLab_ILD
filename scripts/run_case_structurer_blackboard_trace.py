from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tests" / "result"


TRACE_GUIDE = {
    "trace_model": "case_structurer_blackboard_trace",
    "purpose": (
        "Run one data/*.txt input through CaseStructurerAgent, save validation "
        "and correction artifacts, then write the final corrected result into "
        "CaseState via StateWriter."
    ),
    "blackboard_note": (
        "The project does not yet define a separate Blackboard class. In this "
        "trace, CaseState is used as the current case-level blackboard snapshot."
    ),
    "expected_flow": [
        "Choose a txt file from data/ or pass --input.",
        "Run CaseStructurerAgent.run_with_validation().",
        "Save initial result, validation reports, correction report, and corrected result.",
        "Create CaseState for the result case_id.",
        "Write the corrected result through StateWriter.",
        "Save StateWriteResult and CaseState blackboard snapshot.",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run CaseStructurerAgent on a selected data/*.txt file and persist "
            "a CaseState blackboard trace."
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=None,
        help="Input txt file. If omitted, the script prompts from data/*.txt.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory used for interactive txt-file selection.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory where the run_* trace folder is created.",
    )
    parser.add_argument(
        "--case-id",
        default=None,
        help="Optional case_id. If omitted, the agent generates one.",
    )
    parser.add_argument(
        "--input-order",
        type=int,
        default=1,
        help="Input order within the case.",
    )
    parser.add_argument(
        "--parent-input-id",
        default=None,
        help="Optional parent input id for supplemental inputs.",
    )
    return parser.parse_args()


def ensure_repo_on_path() -> None:
    repo_path = str(REPO_ROOT)
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)


def load_runtime_components() -> tuple[type[Any], type[Any], type[Any]]:
    ensure_repo_on_path()
    try:
        from src.agents.case_structurer import CaseStructurerAgent
        from src.state import CaseState, StateWriter
    except ModuleNotFoundError as exc:
        missing = exc.name or str(exc)
        raise RuntimeError(
            "Unable to import runtime dependencies. Install project dependencies "
            f"first, then rerun this script. Missing module: {missing}"
        ) from exc

    return CaseStructurerAgent, CaseState, StateWriter


def read_text_with_fallback(path: Path) -> str:
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
        f"Unable to decode {path} with utf-8/utf-8-sig/gb18030.",
    )


def choose_input_file(data_dir: Path) -> Path:
    input_paths = sorted(data_dir.glob("*.txt"))
    if not input_paths:
        raise FileNotFoundError(f"No .txt files found under {data_dir}.")

    if len(input_paths) == 1:
        selected = input_paths[0]
        print(f"Only one txt file found, using: {selected}")
        return selected

    print("Choose an input txt file:")
    for index, path in enumerate(input_paths, start=1):
        relative = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        print(f"  {index}. {relative}")

    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(input_paths):
                return input_paths[index - 1]
        print(f"Please enter a number from 1 to {len(input_paths)}.")


def resolve_input_path(args: argparse.Namespace) -> Path:
    if args.input is None:
        return choose_input_file(args.data_dir.resolve())

    input_path = args.input
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path

    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if input_path.suffix.lower() != ".txt":
        raise ValueError(f"Input file must be a .txt file: {input_path}")
    return input_path


def make_output_dir(output_root: Path) -> Path:
    run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_dir = output_root / f"run_{run_tag}_case_structurer_blackboard_trace"
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def to_jsonable(payload: Any) -> Any:
    if hasattr(payload, "model_dump"):
        return payload.model_dump(mode="json")
    if isinstance(payload, list):
        return [to_jsonable(item) for item in payload]
    if isinstance(payload, tuple):
        return [to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {str(key): to_jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Path):
        return str(payload)
    return payload


def write_json(output_dir: Path, file_name: str, payload: Any) -> Path:
    path = output_dir / file_name
    path.write_text(
        json.dumps(to_jsonable(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def count_by_severity(issues: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        severity = getattr(issue, "severity", None)
        severity_value = getattr(severity, "value", severity)
        key = str(severity_value or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def build_summary(
    input_path: Path,
    output_dir: Path,
    validation_bundle: Any,
    write_result: Any,
    state: Any,
) -> dict[str, Any]:
    corrected_result = validation_bundle.corrected_result
    initial_report = validation_bundle.initial_validation_report
    final_report = validation_bundle.final_validation_report

    return {
        "trace_model": "case_structurer_blackboard_trace",
        "input_path": input_path,
        "output_dir": output_dir,
        "case_id": corrected_result.input.case_id,
        "input_id": corrected_result.input.input_id,
        "agent_validation": {
            "initial_is_valid": initial_report.is_valid,
            "initial_issue_count": len(initial_report.issues),
            "initial_issue_counts_by_severity": count_by_severity(
                initial_report.issues
            ),
            "correction_applied_count": (
                validation_bundle.correction_report.applied_count
            ),
            "correction_skipped_count": (
                validation_bundle.correction_report.skipped_count
            ),
            "final_is_valid": final_report.is_valid,
            "final_issue_count": len(final_report.issues),
            "final_issue_counts_by_severity": count_by_severity(final_report.issues),
        },
        "state_write": {
            "accepted": write_result.accepted,
            "status": write_result.status,
            "message": write_result.message,
            "event_id": write_result.write_event.event_id,
        },
        "blackboard_snapshot_counts": {
            "raw_inputs": len(state.raw_inputs),
            "case_structuring_results": len(state.case_structuring_results),
            "source_span_validation_correction_results": len(
                state.source_span_validation_correction_results
            ),
            "write_events": len(state.write_events),
        },
    }


def main() -> int:
    args = parse_args()
    input_path = resolve_input_path(args)
    output_dir = make_output_dir(args.output_root.resolve())

    print(f"Input: {input_path}")
    print(f"Trace output: {output_dir}")

    write_json(
        output_dir,
        "00_trace_guide.json",
        {
            **TRACE_GUIDE,
            "selected_input_path": input_path,
            "requested_case_id": args.case_id,
            "input_order": args.input_order,
            "parent_input_id": args.parent_input_id,
        },
    )

    raw_text = read_text_with_fallback(input_path)
    write_json(
        output_dir,
        "01_selected_raw_input.json",
        {
            "input_path": input_path,
            "requested_case_id": args.case_id,
            "input_order": args.input_order,
            "parent_input_id": args.parent_input_id,
            "raw_text": raw_text,
        },
    )

    try:
        CaseStructurerAgent, CaseState, StateWriter = load_runtime_components()
        agent = CaseStructurerAgent()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(
            "ERROR: Unable to initialize CaseStructurerAgent. "
            "Check CHATANYWHERE_API_KEY and configs/agents.yaml.",
            file=sys.stderr,
        )
        print(f"Detail: {exc}", file=sys.stderr)
        return 2

    validation_bundle = agent.run_with_validation(
        raw_text=raw_text,
        case_id=args.case_id,
        input_order=args.input_order,
        parent_input_id=args.parent_input_id,
    )

    write_json(
        output_dir,
        "02_initial_case_structuring_result.json",
        validation_bundle.initial_result,
    )
    write_json(
        output_dir,
        "03_initial_source_span_validation_report.json",
        validation_bundle.initial_validation_report,
    )
    write_json(
        output_dir,
        "04_source_span_correction_report.json",
        validation_bundle.correction_report,
    )
    write_json(
        output_dir,
        "05_corrected_case_structuring_result.json",
        validation_bundle.corrected_result,
    )
    write_json(
        output_dir,
        "06_final_source_span_validation_report.json",
        validation_bundle.final_validation_report,
    )

    state = CaseState(case_id=validation_bundle.corrected_result.input.case_id)
    write_result = StateWriter().write_case_structuring_result(
        state=state,
        result=validation_bundle.corrected_result,
        agent_name="case_structurer",
    )

    write_json(output_dir, "07_state_write_result.json", write_result)
    write_json(output_dir, "08_case_state_blackboard_snapshot.json", state)

    summary = build_summary(
        input_path=input_path,
        output_dir=output_dir,
        validation_bundle=validation_bundle,
        write_result=write_result,
        state=state,
    )
    write_json(output_dir, "09_run_summary.json", summary)

    print("Done.")
    print(f"case_id: {summary['case_id']}")
    print(f"input_id: {summary['input_id']}")
    print(
        "agent final source-span valid: "
        f"{summary['agent_validation']['final_is_valid']}"
    )
    print(
        "state write: "
        f"{summary['state_write']['status']} - {summary['state_write']['message']}"
    )
    print(f"blackboard snapshot: {output_dir / '08_case_state_blackboard_snapshot.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
