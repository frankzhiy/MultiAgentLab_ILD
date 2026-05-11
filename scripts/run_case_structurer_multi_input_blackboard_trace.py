from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tests" / "result"


TRACE_GUIDE = {
    "trace_model": "case_structurer_multi_input_blackboard_trace",
    "purpose": (
        "Run multiple txt inputs through CaseStructurerAgent as sequential "
        "inputs for one case, save per-round validation/correction artifacts, "
        "and write every accepted corrected result into one shared CaseState."
    ),
    "blackboard_note": (
        "The project does not yet define a separate Blackboard class. In this "
        "trace, CaseState is used as the current case-level blackboard snapshot."
    ),
    "important_limit": (
        "Current CaseStructurerAgent calls do not read prior CaseState content. "
        "This script tests repeated input ingestion and state accumulation under "
        "one case_id, not context-aware extraction that uses previous rounds as "
        "LLM context."
    ),
    "expected_flow": [
        "Choose one txt file from data/ or pass --inputs.",
        "Run each file in order with the same case_id.",
        "In interactive mode, choose the next supplemental txt only after the current round finishes.",
        "Use input_order to mark the sequence.",
        "Optionally set parent_input_id to the previous accepted input_id.",
        "Save per-round initial result, validation reports, correction report, and corrected result.",
        "Write each corrected result through StateWriter into one CaseState.",
        "Save a blackboard snapshot after each round and a final snapshot.",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run multiple CaseStructurerAgent inputs into one CaseState "
            "blackboard trace."
        )
    )
    parser.add_argument(
        "-i",
        "--inputs",
        nargs="+",
        type=Path,
        default=None,
        help=(
            "Input txt files in round order. If omitted, the script runs "
            "interactive round-by-round selection from data/*.txt."
        ),
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
        help=(
            "Optional case_id shared by all rounds. If omitted, round 1 "
            "generates one and later rounds reuse it."
        ),
    )
    parser.add_argument(
        "--start-input-order",
        type=int,
        default=1,
        help="Input order assigned to the first selected input.",
    )
    parser.add_argument(
        "--no-parent-chain",
        action="store_true",
        help=(
            "Do not set parent_input_id for later rounds. By default, each "
            "later round points to the previous accepted input_id."
        ),
    )
    parser.add_argument(
        "--continue-on-reject",
        action="store_true",
        help=(
            "Continue later rounds even if a StateWriter write is rejected. "
            "By default, the script stops after the first rejected write."
        ),
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


def choose_input_file(data_dir: Path, round_index: int) -> Path:
    input_paths = sorted(data_dir.glob("*.txt"))
    if not input_paths:
        raise FileNotFoundError(f"No .txt files found under {data_dir}.")

    print(f"Choose input txt file for round {round_index}:")
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


def ask_continue() -> bool:
    while True:
        choice = input("Add another supplemental input for this case? [y/N]: ")
        normalized = choice.strip().lower()
        if normalized in {"", "n", "no"}:
            return False
        if normalized in {"y", "yes"}:
            return True
        print("Please enter y or n.")


def resolve_input_paths(args: argparse.Namespace) -> list[Path] | None:
    if args.inputs is None:
        return None

    resolved_paths: list[Path] = []
    for input_path in args.inputs:
        if not input_path.is_absolute():
            input_path = REPO_ROOT / input_path

        input_path = input_path.resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")
        if input_path.suffix.lower() != ".txt":
            raise ValueError(f"Input file must be a .txt file: {input_path}")
        resolved_paths.append(input_path)

    if not resolved_paths:
        raise ValueError("At least one input file is required.")
    return resolved_paths


def make_output_dir(output_root: Path) -> Path:
    run_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_dir = output_root / f"run_{run_tag}_case_structurer_multi_input_blackboard_trace"
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def safe_name(path: Path) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem).strip("._")
    return cleaned or "input"


def make_round_dir(output_dir: Path, round_index: int, input_path: Path) -> Path:
    round_dir = output_dir / f"round_{round_index:02d}_{safe_name(input_path)}"
    round_dir.mkdir(parents=True, exist_ok=False)
    return round_dir


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


def round_summary(
    round_index: int,
    input_path: Path,
    input_order: int,
    requested_parent_input_id: str | None,
    validation_bundle: Any,
    write_result: Any,
    state: Any,
) -> dict[str, Any]:
    corrected_result = validation_bundle.corrected_result
    initial_report = validation_bundle.initial_validation_report
    final_report = validation_bundle.final_validation_report

    return {
        "round": round_index,
        "input_path": input_path,
        "input_order": input_order,
        "requested_parent_input_id": requested_parent_input_id,
        "case_id": corrected_result.input.case_id,
        "input_id": corrected_result.input.input_id,
        "stage_context": corrected_result.stage_context,
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
        "blackboard_snapshot_counts_after_round": {
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
    input_paths = resolve_input_paths(args)
    output_dir = make_output_dir(args.output_root.resolve())

    if input_paths is None:
        print("Interactive multi-input mode.")
        print(f"Data directory: {args.data_dir.resolve()}")
    else:
        print("Inputs:")
        for index, input_path in enumerate(input_paths, start=1):
            print(f"  {index}. {input_path}")
    print(f"Trace output: {output_dir}")

    write_json(
        output_dir,
        "00_trace_guide.json",
        {
            **TRACE_GUIDE,
            "interactive_mode": input_paths is None,
            "selected_input_paths": input_paths,
            "data_dir": args.data_dir.resolve(),
            "requested_case_id": args.case_id,
            "start_input_order": args.start_input_order,
            "parent_chain_enabled": not args.no_parent_chain,
            "continue_on_reject": args.continue_on_reject,
        },
    )

    try:
        CaseStructurerAgent, CaseState, StateWriter = load_runtime_components()
        agent = CaseStructurerAgent()
        state_writer = StateWriter()
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

    state = None
    active_case_id = args.case_id
    previous_accepted_input_id: str | None = None
    summaries: list[dict[str, Any]] = []
    selected_input_paths: list[Path] = []

    round_index = 0
    while True:
        if input_paths is None:
            if round_index > 0 and not ask_continue():
                break
            input_path = choose_input_file(args.data_dir.resolve(), round_index + 1)
        else:
            if round_index >= len(input_paths):
                break
            input_path = input_paths[round_index]

        selected_input_paths.append(input_path)
        input_order = args.start_input_order + round_index
        round_index += 1
        parent_input_id = None
        if not args.no_parent_chain and round_index > 1:
            parent_input_id = previous_accepted_input_id

        round_dir = make_round_dir(output_dir, round_index, input_path)
        raw_text = read_text_with_fallback(input_path)
        print(
            f"Round {round_index}: {input_path.name} "
            f"(input_order={input_order}, parent_input_id={parent_input_id})"
        )

        write_json(
            round_dir,
            "01_selected_raw_input.json",
            {
                "input_path": input_path,
                "case_id": active_case_id,
                "input_order": input_order,
                "parent_input_id": parent_input_id,
                "raw_text": raw_text,
            },
        )

        validation_bundle = agent.run_with_validation(
            raw_text=raw_text,
            case_id=active_case_id,
            input_order=input_order,
            parent_input_id=parent_input_id,
        )

        corrected_result = validation_bundle.corrected_result
        if active_case_id is None:
            active_case_id = corrected_result.input.case_id

        if state is None:
            state = CaseState(case_id=corrected_result.input.case_id)

        write_json(
            round_dir,
            "02_initial_case_structuring_result.json",
            validation_bundle.initial_result,
        )
        write_json(
            round_dir,
            "03_initial_source_span_validation_report.json",
            validation_bundle.initial_validation_report,
        )
        write_json(
            round_dir,
            "04_source_span_correction_report.json",
            validation_bundle.correction_report,
        )
        write_json(
            round_dir,
            "05_corrected_case_structuring_result.json",
            corrected_result,
        )
        write_json(
            round_dir,
            "06_final_source_span_validation_report.json",
            validation_bundle.final_validation_report,
        )

        write_result = state_writer.write_case_structuring_result(
            state=state,
            result=corrected_result,
            agent_name="case_structurer",
        )

        write_json(round_dir, "07_state_write_result.json", write_result)
        write_json(round_dir, "08_blackboard_snapshot_after_round.json", state)

        summary = round_summary(
            round_index=round_index,
            input_path=input_path,
            input_order=input_order,
            requested_parent_input_id=parent_input_id,
            validation_bundle=validation_bundle,
            write_result=write_result,
            state=state,
        )
        summaries.append(summary)
        write_json(round_dir, "09_round_summary.json", summary)

        print(
            "  write: "
            f"{write_result.status} - {write_result.message}"
        )

        if write_result.accepted:
            previous_accepted_input_id = corrected_result.input.input_id
        elif not args.continue_on_reject:
            print("Stopping after rejected write. Use --continue-on-reject to continue.")
            break

    if state is None:
        raise RuntimeError("No rounds were executed.")

    final_summary = {
        "trace_model": "case_structurer_multi_input_blackboard_trace",
        "output_dir": output_dir,
        "interactive_mode": input_paths is None,
        "selected_input_paths": selected_input_paths,
        "case_id": state.case_id,
        "round_count_requested": len(input_paths) if input_paths is not None else None,
        "round_count_executed": len(summaries),
        "rounds": summaries,
        "final_blackboard_snapshot_counts": {
            "raw_inputs": len(state.raw_inputs),
            "case_structuring_results": len(state.case_structuring_results),
            "source_span_validation_correction_results": len(
                state.source_span_validation_correction_results
            ),
            "write_events": len(state.write_events),
        },
    }

    write_json(output_dir, "98_final_case_state_blackboard_snapshot.json", state)
    write_json(output_dir, "99_run_summary.json", final_summary)

    print("Done.")
    print(f"case_id: {state.case_id}")
    if input_paths is None:
        print(f"rounds executed: {len(summaries)}")
    else:
        print(f"rounds executed: {len(summaries)} / {len(input_paths)}")
    print(
        "final blackboard counts: "
        f"raw_inputs={len(state.raw_inputs)}, "
        f"case_structuring_results={len(state.case_structuring_results)}, "
        f"write_events={len(state.write_events)}"
    )
    print(
        "final blackboard snapshot: "
        f"{output_dir / '98_final_case_state_blackboard_snapshot.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
