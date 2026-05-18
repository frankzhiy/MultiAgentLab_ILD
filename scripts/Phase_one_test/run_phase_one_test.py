from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from threading import Event, Thread
from time import perf_counter
from typing import Any

from phase_one_common import (
    display_path as _display_path,
    format_duration,
    obj_field,
    write_json,
    write_text,
)
from phase_one_outputs import write_outputs
from phase_one_summary import build_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "results" / "phase_one_test"
TEXT_EXTENSIONS = {".txt", ".md", ".json", ".csv"}


class Style:
    reset = "\033[0m"
    bold = "\033[1m"
    dim = "\033[2m"
    green = "\033[32m"
    blue = "\033[34m"
    cyan = "\033[36m"
    red = "\033[31m"


def use_color() -> bool:
    return sys.stdout.isatty() and os.getenv("NO_COLOR") is None


def color(text: str, code: str) -> str:
    if not use_color():
        return text
    return f"{code}{text}{Style.reset}"


def display_path(path: Path) -> str:
    return _display_path(path, REPO_ROOT)


def ensure_repo_on_path() -> None:
    repo_path = str(REPO_ROOT)
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)


def load_runtime_components() -> tuple[type[Any], type[Any], type[Any]]:
    ensure_repo_on_path()
    try:
        from src.agents.case_structurer import CaseStructurerAgent
        from src.agents.evidence_tree_structurer import EvidenceTreeStructurerAgent
        from src.llm.chatanywhere_client import ChatAnywhereClient
    except ModuleNotFoundError as exc:
        missing = exc.name or str(exc)
        raise RuntimeError(
            "Unable to import runtime dependencies. Install project dependencies "
            f"first, then rerun this script. Missing module: {missing}"
        ) from exc

    return CaseStructurerAgent, EvidenceTreeStructurerAgent, ChatAnywhereClient


class LiveTimer:
    def __init__(self, label: str, refresh_seconds: float = 0.8) -> None:
        self.label = label
        self.refresh_seconds = refresh_seconds
        self.elapsed_seconds = 0.0
        self._started_at = 0.0
        self._stop_event = Event()
        self._thread: Thread | None = None

    def __enter__(self) -> "LiveTimer":
        self._started_at = perf_counter()
        self._render()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.elapsed_seconds = perf_counter() - self._started_at
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.refresh_seconds + 0.2)
        self._clear_line()
        status = color("failed", Style.red) if exc_type else color("done", Style.green)
        print(f"  {status} {self.label} in {format_duration(self.elapsed_seconds)}")
        return False

    def _loop(self) -> None:
        while not self._stop_event.wait(self.refresh_seconds):
            self.elapsed_seconds = perf_counter() - self._started_at
            self._render()

    def _render(self) -> None:
        dots = "." * (int(perf_counter() - self._started_at) % 4)
        print(
            f"\r  {color('running', Style.cyan)} {self.label}{dots:<3} "
            f"{format_duration(perf_counter() - self._started_at)}",
            end="",
            flush=True,
        )

    @staticmethod
    def _clear_line() -> None:
        print("\r" + " " * 100 + "\r", end="", flush=True)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_readable_text_file(path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    try:
        with path.open("r", encoding="utf-8") as file:
            file.read(1)
    except (OSError, UnicodeDecodeError):
        return False
    return True


def preview_text(path: Path, limit: int = 72) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    text = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1]}..."


def find_data_files(data_dir: Path) -> list[Path]:
    if not data_dir.exists():
        return []
    files = [
        path.resolve()
        for path in data_dir.rglob("*")
        if not any(part.startswith(".") for part in path.relative_to(data_dir).parts)
        and is_readable_text_file(path)
    ]
    return sorted(files, key=lambda item: display_path(item).lower())


def print_banner(title: str, subtitle: str | None = None) -> None:
    width = max(72, len(title) + 8)
    print(color("╭" + "─" * (width - 2) + "╮", Style.blue))
    print(color("│", Style.blue) + f" {color(title, Style.bold):<{width - 4}} " + color("│", Style.blue))
    if subtitle:
        print(color("│", Style.blue) + f" {subtitle:<{width - 4}} " + color("│", Style.blue))
    print(color("╰" + "─" * (width - 2) + "╯", Style.blue))


def choose_file(files: list[Path]) -> Path:
    print()
    print(color("Available data inputs", Style.bold))
    print(color("─" * 96, Style.dim))
    print(f"{'#':>3}  {'file':<28} {'size':>8}  preview")
    print(color("─" * 96, Style.dim))
    for index, path in enumerate(files, start=1):
        size = f"{path.stat().st_size:,}B"
        print(f"{index:>3}  {display_path(path):<28.28} {size:>8}  {preview_text(path)}")
    print(color("─" * 96, Style.dim))

    while True:
        choice = input("Select input number, or q to quit: ").strip().lower()
        if choice == "q":
            raise KeyboardInterrupt
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(files):
                return files[index - 1]
        print(f"Please enter a number from 1 to {len(files)}, or q.")


def selected_file_payload(
    *,
    selected_file: Path,
    raw_text: str,
    case_id: str | None,
    input_order: int,
    parent_input_id: str | None,
    created_at: str,
) -> dict[str, Any]:
    return {
        "selected_file": display_path(selected_file),
        "absolute_path": str(selected_file),
        "file_name": selected_file.name,
        "byte_size": selected_file.stat().st_size,
        "character_count": len(raw_text),
        "case_id_passed_to_case_structurer": case_id,
        "input_order": input_order,
        "parent_input_id": parent_input_id,
        "created_at": created_at,
    }


def initialize_agents() -> tuple[Any, Any]:
    CaseStructurerAgent, EvidenceTreeStructurerAgent, ChatAnywhereClient = load_runtime_components()
    llm_client = ChatAnywhereClient()
    return CaseStructurerAgent(llm_client=llm_client), EvidenceTreeStructurerAgent(llm_client=llm_client)


def run_stage(label: str, callback: Any) -> tuple[Any, float]:
    timer = LiveTimer(label)
    with timer:
        result = callback()
    return result, timer.elapsed_seconds


def resolve_selected_file(args: argparse.Namespace, files: list[Path]) -> Path:
    if args.file is None:
        return choose_file(files)
    selected = Path(args.file)
    if not selected.is_absolute():
        selected = (REPO_ROOT / selected).resolve()
    if selected not in files and not is_readable_text_file(selected):
        raise FileNotFoundError(f"Selected file is not a readable text input: {selected}")
    return selected


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phase One end-to-end: Case Structurer -> Evidence Tree Structurer, "
            "then write compact JSON and readable HTML outputs."
        )
    )
    parser.add_argument("--file", help="Input file path. If omitted, choose from CLI.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--case-id", default=None, help="Optional existing case_id.")
    parser.add_argument("--input-order", type=int, default=1)
    parser.add_argument("--parent-input-id", default=None)
    parser.add_argument("--list-only", action="store_true")
    return parser.parse_args(argv)


def evidence_tree_structurer_progress_printer(tree_timer: LiveTimer):
    def progress(step: str, elapsed_seconds: float) -> None:
        LiveTimer._clear_line()
        print(
            "    "
            + color("done", Style.green)
            + f" {step} in {format_duration(elapsed_seconds)}"
        )
        tree_timer._render()

    return progress


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        data_dir = (REPO_ROOT / data_dir).resolve()
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (REPO_ROOT / output_root).resolve()

    print_banner("Phase One Test Runner", "Case Structurer -> Evidence Tree Structurer")

    files = find_data_files(data_dir)
    if not files:
        print(color(f"No readable input files found under {data_dir}", Style.red))
        return 1
    if args.list_only:
        for path in files:
            print(display_path(path))
        return 0

    try:
        selected_file = resolve_selected_file(args, files)
    except KeyboardInterrupt:
        print("\nNo input selected.")
        return 0
    except Exception as exc:
        print(color(f"Input selection failed: {exc}", Style.red), file=sys.stderr)
        return 1

    raw_text = selected_file.read_text(encoding="utf-8")
    created_at = utc_iso()
    timestamp = utc_stamp()
    pending_dir = output_root / f"pending_{timestamp}"
    pending_dir.mkdir(parents=True, exist_ok=False)

    selected_payload = selected_file_payload(
        selected_file=selected_file,
        raw_text=raw_text,
        case_id=args.case_id,
        input_order=args.input_order,
        parent_input_id=args.parent_input_id,
        created_at=created_at,
    )
    write_text(pending_dir / "raw_input.txt", raw_text)
    write_json(pending_dir / "selected_file.json", selected_payload)

    print()
    print(f"Selected: {color(display_path(selected_file), Style.bold)}")
    print(f"Output:   {pending_dir}")
    print()

    try:
        case_structurer, evidence_tree_structurer = initialize_agents()
    except Exception as exc:
        write_json(pending_dir / "error.json", {"stage": "startup", "type": type(exc).__name__, "message": str(exc)})
        print(color("Failed to initialize agents.", Style.red), file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    total_start = perf_counter()
    try:
        case_bundle, case_seconds = run_stage(
            "Case Structurer",
            lambda: case_structurer.run_with_validation(
                raw_text=raw_text,
                case_id=args.case_id,
                input_order=args.input_order,
                parent_input_id=args.parent_input_id,
            ),
        )
        corrected_result = obj_field(case_bundle, "corrected_result")
        if corrected_result is None:
            raise RuntimeError("Case Structurer did not return corrected_result.")

        case_id = obj_field(obj_field(corrected_result, "input"), "case_id")
        output_dir = output_root / f"{case_id}_{timestamp}"
        if output_dir.exists():
            suffix = datetime.now(timezone.utc).strftime("%f")
            output_dir = output_root / f"{case_id}_{timestamp}_{suffix}"
        pending_dir.rename(output_dir)

        tree_timer = LiveTimer("Evidence Tree Structurer")
        with tree_timer:
            tree_structuring_bundle = evidence_tree_structurer.run_with_validation(
                corrected_result,
                progress_callback=evidence_tree_structurer_progress_printer(tree_timer),
            )
        tree_seconds = tree_timer.elapsed_seconds
        tree_structuring_result = obj_field(tree_structuring_bundle, "tree_structuring_result")
        if tree_structuring_result is None:
            raise RuntimeError("Evidence Tree Structurer did not return tree_structuring_result.")

        total_seconds = perf_counter() - total_start
        tree_result = obj_field(tree_structuring_bundle, "evidence_tree_build_result")
        assertion_resolution = obj_field(tree_structuring_bundle, "clinical_assertion_resolution")
        tree_structurer_timings = obj_field(tree_structuring_bundle, "pipeline_timings_seconds", {})

        durations = {
            "case_structurer": case_seconds,
            "evidence_tree_structurer": tree_seconds,
            **{f"evidence_tree_structurer.{step}": seconds for step, seconds in tree_structurer_timings.items()},
            "total": total_seconds,
        }
        summary = build_summary(
            selected_file=selected_file,
            repo_root=REPO_ROOT,
            created_at=created_at,
            corrected_result=corrected_result,
            tree_structuring_result=tree_structuring_result,
            tree_structuring_validation_report=obj_field(tree_structuring_bundle, "validation_report"),
            assertion_resolution=assertion_resolution,
            tree_result=tree_result,
            durations=durations,
        )

        write_outputs(
            output_dir=output_dir,
            raw_text=raw_text,
            selected_payload=selected_payload,
            summary=summary,
            case_bundle=case_bundle,
            corrected_result=corrected_result,
            tree_structuring_bundle=tree_structuring_bundle,
            tree_structuring_result=tree_structuring_result,
            tree_result=tree_result,
        )
    except Exception as exc:
        target_dir = locals().get("output_dir", pending_dir)
        write_json(target_dir / "error.json", {"stage": "runtime", "type": type(exc).__name__, "message": str(exc)})
        print(color(f"Run failed: {type(exc).__name__}: {exc}", Style.red), file=sys.stderr)
        print(f"Partial outputs: {target_dir}", file=sys.stderr)
        return 1

    print()
    print(color("Phase One run completed.", Style.green))
    print(f"case_id:     {summary['case_id']}")
    print(f"input_id:    {summary['input_id']}")
    print(f"duration:    {summary['durations_human']['total']}")
    print(f"report:      {output_dir / 'report.html'}")
    print(f"summary:     {output_dir / 'summary.md'}")
    print(f"json dir:    {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
