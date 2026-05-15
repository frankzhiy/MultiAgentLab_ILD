from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import os
import sys
from threading import Event, Thread
from time import perf_counter
from os import walk
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_RESULT_ROOT = REPO_ROOT / "results" / "phase1_trace"
TEXT_EXTENSIONS = {".txt", ".md", ".json", ".csv"}

MULTI_ROUND_NOTE = (
    "Multi-round support here means the same case_id is reused across rounds "
    "with increasing input_order and parent_input_id. Evidence Atomizer remains "
    "stateless per round. Cross-round merging, belief revision, and update "
    "management belong to later phases."
)


def ensure_repo_on_path() -> None:
    repo_path = str(REPO_ROOT)
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)


def load_runtime_components() -> tuple[type[Any], type[Any], type[Any], type[Any]]:
    ensure_repo_on_path()
    try:
        from src.agents.case_structurer import CaseStructurerAgent
        from src.agents.attribute_extractor import AttributeExtractorAgent
        from src.agents.evidence_atomizer import EvidenceAtomizerAgent
        from src.llm.chatanywhere_client import ChatAnywhereClient
    except ModuleNotFoundError as exc:
        missing = exc.name or str(exc)
        raise RuntimeError(
            "Unable to import runtime dependencies. Install project dependencies "
            f"first, then rerun this script. Missing module: {missing}"
        ) from exc

    return (
        CaseStructurerAgent,
        AttributeExtractorAgent,
        EvidenceAtomizerAgent,
        ChatAnywhereClient,
    )


def make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"

    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)} min {remainder:.1f} s"


class LiveTimer:
    """Render a single-line elapsed timer while a blocking stage runs."""

    def __init__(self, label: str, refresh_seconds: float = 1.0) -> None:
        self.label = label
        self.refresh_seconds = refresh_seconds
        self.elapsed_seconds = 0.0
        self._started_at = 0.0
        self._stop_event = Event()
        self._thread: Thread | None = None

    def __enter__(self) -> "LiveTimer":
        self._started_at = perf_counter()
        self._render()
        self._thread = Thread(target=self._render_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.elapsed_seconds = perf_counter() - self._started_at
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.refresh_seconds + 0.2)
        self._clear_line()

        status = "failed after" if exc_type is not None else "completed in"
        print(f"{self.label} {status} {format_duration(self.elapsed_seconds)}.")
        return False

    def _render_loop(self) -> None:
        while not self._stop_event.wait(self.refresh_seconds):
            self.elapsed_seconds = perf_counter() - self._started_at
            self._render()

    def _render(self) -> None:
        print(
            f"\r{self.label} running... elapsed "
            f"{format_duration(perf_counter() - self._started_at)}",
            end="",
            flush=True,
        )

    @staticmethod
    def _clear_line() -> None:
        print("\r" + " " * 100 + "\r", end="", flush=True)


def is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def is_readable_file(path: Path) -> bool:
    if not path.is_file() or not os.access(path, os.R_OK):
        return False
    try:
        with path.open("rb") as file:
            file.read(1)
    except OSError:
        return False
    return True


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def find_data_files(data_dir: Path) -> list[Path]:
    if not data_dir.exists() or not data_dir.is_dir():
        return []

    files: list[Path] = []
    for dirpath, dirnames, filenames in walk(data_dir):
        dirnames[:] = [name for name in dirnames if not name.startswith(".")]
        current_dir = Path(dirpath)
        for filename in filenames:
            if filename.startswith("."):
                continue
            path = current_dir / filename
            try:
                relative = path.relative_to(data_dir)
            except ValueError:
                continue
            if is_hidden_path(relative):
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if is_readable_file(path):
                files.append(path.resolve())

    return sorted(files, key=lambda item: display_path(item).lower())


def choose_file(files: list[Path]) -> Path:
    print("\nAvailable data files:")
    for index, path in enumerate(files, start=1):
        print(f"[{index}] {display_path(path)}")

    while True:
        choice = input("Select one file by number, or q to quit: ").strip().lower()
        if choice == "q":
            raise KeyboardInterrupt("User quit file selection.")
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(files):
                return files[index - 1]
        print(f"Please enter a number from 1 to {len(files)}, or q to quit.")


def ask_continue() -> bool:
    print("\nContinue adding another input for the same case?")
    print("[1] Continue")
    print("[2] Finish")
    while True:
        choice = input("Select 1 or 2: ").strip().lower()
        if choice == "1":
            return True
        if choice in {"2", "q"}:
            return False
        print("Please enter 1 to continue or 2 to finish.")


def read_utf8_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def model_to_jsonable(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(mode="json")
        except Exception:
            return str(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return model_to_jsonable(asdict(obj))
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(key): model_to_jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [model_to_jsonable(item) for item in obj]
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if hasattr(obj, "__dict__"):
        try:
            return model_to_jsonable(vars(obj))
        except Exception:
            return str(obj)
    return str(obj)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    jsonable = model_to_jsonable(data)
    path.write_text(
        json.dumps(jsonable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def issue_counts_by_severity(report: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in getattr(report, "issues", []) or []:
        severity = getattr(issue, "severity", None)
        key = str(getattr(severity, "value", severity) or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def issue_counts_by_code(report: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in getattr(report, "issues", []) or []:
        code = str(getattr(issue, "code", None) or "unknown")
        counts[code] = counts.get(code, 0) + 1
    return counts


def issue_codes(report: Any) -> list[str]:
    return sorted(issue_counts_by_code(report))


def safe_validation_bundle_payload(bundle: Any) -> Any:
    full_payload = model_to_jsonable(bundle)
    try:
        json.dumps(full_payload, ensure_ascii=False)
        return full_payload
    except TypeError:
        return {
            "corrected_result": model_to_jsonable(
                getattr(bundle, "corrected_result", None)
            ),
            "validation_report": model_to_jsonable(
                getattr(bundle, "validation_report", None)
            ),
            "initial_validation_report": model_to_jsonable(
                getattr(bundle, "initial_validation_report", None)
            ),
            "correction_report": model_to_jsonable(
                getattr(bundle, "correction_report", None)
            ),
            "final_report": model_to_jsonable(
                getattr(bundle, "final_report", None)
                or getattr(bundle, "final_validation_report", None)
            ),
        }


def exception_payload(stage: str, exc: BaseException) -> dict[str, str]:
    return {
        "stage": stage,
        "exception_type": type(exc).__name__,
        "message": str(exc),
    }


def make_selected_file_payload(
    *,
    selected_file: Path,
    round_index: int,
    input_order: int,
    parent_input_id: str | None,
    case_id: str | None,
) -> dict[str, Any]:
    return {
        "original_file_path": str(selected_file),
        "display_path": display_path(selected_file),
        "file_name": selected_file.name,
        "round_number": round_index,
        "input_order": input_order,
        "parent_input_id": parent_input_id,
        "case_id_passed_to_case_structurer": case_id,
    }


def make_round_dir(result_root: Path, round_index: int) -> Path:
    round_dir = result_root / f"round_{round_index:03d}"
    round_dir.mkdir(parents=True, exist_ok=True)
    return round_dir


def maybe_promote_result_root(
    current_root: Path,
    case_id: str,
    timestamp: str,
) -> Path:
    target_root = DEFAULT_RESULT_ROOT / f"{case_id}_{timestamp}"
    if current_root == target_root:
        return current_root
    if target_root.exists():
        suffix = datetime.now(timezone.utc).strftime("%f")
        target_root = DEFAULT_RESULT_ROOT / f"{case_id}_{timestamp}_{suffix}"
    current_root.rename(target_root)
    return target_root


def enum_text(value: Any) -> str:
    if value is None:
        return ""
    return str(getattr(value, "value", value))


def markdown_cell(value: Any) -> str:
    text = enum_text(value)
    text = text.replace("\n", " ").replace("\r", " ")
    text = text.replace("|", "\\|")
    return text.strip()


def object_field(obj: Any, field_name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(field_name, default)
    return getattr(obj, field_name, default)


def object_list_field(obj: Any, field_name: str) -> list[Any]:
    value = object_field(obj, field_name, [])
    if value is None:
        return []
    return list(value)


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(markdown_cell(value) for value in values) + " |"


def empty_markdown_row(column_count: int, message: str) -> str:
    values = [""] * column_count
    if values:
        values[0] = message
    return markdown_row(values)


def join_markdown_values(values: Any, separator: str = ", ") -> str:
    if values is None:
        return ""
    if isinstance(values, str):
        return values
    return separator.join(enum_text(value) for value in values)


def source_span_ids(spans: list[Any]) -> str:
    return join_markdown_values(
        [
            object_field(span, "span_id")
            for span in spans
            if object_field(span, "span_id")
        ]
    )


def source_span_text(spans: list[Any]) -> str:
    return " / ".join(
        enum_text(object_field(span, "quoted_text"))
        for span in spans
        if object_field(span, "quoted_text")
    )


def render_stage_context_table(stage_context: Any) -> list[str]:
    lines = [
        "### Stage Context",
        "",
        "| stage_id | stage_order | stage_type | relation_to_previous_stage | previous_stage_id | is_initial_stage | classification_confidence | classification_basis |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if stage_context is None:
        lines.append(empty_markdown_row(8, "No stage context produced."))
        return lines

    lines.append(
        markdown_row(
            [
                object_field(stage_context, "stage_id"),
                object_field(stage_context, "stage_order"),
                object_field(stage_context, "stage_type"),
                object_field(stage_context, "relation_to_previous_stage"),
                object_field(stage_context, "previous_stage_id"),
                object_field(stage_context, "is_initial_stage"),
                object_field(stage_context, "classification_confidence"),
                object_field(stage_context, "classification_basis"),
            ]
        )
    )
    return lines


def render_clinical_sections_table(sections: list[Any]) -> list[str]:
    lines = [
        "### Clinical Sections",
        "",
        "| section_id | section_order | section_type | title | parent_section_id | classification_confidence | source_span_ids | normalized_text |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not sections:
        lines.append(empty_markdown_row(8, "No clinical sections produced."))
        return lines

    for section in sections:
        spans = object_list_field(section, "source_spans")
        lines.append(
            markdown_row(
                [
                    object_field(section, "section_id"),
                    object_field(section, "section_order"),
                    object_field(section, "section_type"),
                    object_field(section, "title"),
                    object_field(section, "parent_section_id"),
                    object_field(section, "classification_confidence"),
                    source_span_ids(spans),
                    object_field(section, "normalized_text"),
                ]
            )
        )
    return lines


def render_structured_items_table(items: list[Any]) -> list[str]:
    lines = [
        "### Structured Clinical Items",
        "",
        "| item_id | item_order | section_id | item_type | label | temporality | certainty | negation | classification_confidence | source_span_ids | source_text |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not items:
        lines.append(empty_markdown_row(11, "No structured clinical items produced."))
        return lines

    for item in items:
        spans = object_list_field(item, "source_spans")
        lines.append(
            markdown_row(
                [
                    object_field(item, "item_id"),
                    object_field(item, "item_order"),
                    object_field(item, "section_id"),
                    object_field(item, "item_type"),
                    object_field(item, "label"),
                    object_field(item, "temporality"),
                    object_field(item, "certainty"),
                    object_field(item, "negation"),
                    object_field(item, "classification_confidence"),
                    source_span_ids(spans),
                    source_span_text(spans),
                ]
            )
        )
    return lines


def render_structuring_warnings_table(warnings: list[Any]) -> list[str]:
    lines = [
        "### Structuring Warnings",
        "",
        "| severity | code | message | related_object_id |",
        "| --- | --- | --- | --- |",
    ]
    if not warnings:
        lines.append(empty_markdown_row(4, "No structuring warnings produced."))
        return lines

    for warning in warnings:
        lines.append(
            markdown_row(
                [
                    object_field(warning, "severity"),
                    object_field(warning, "code"),
                    object_field(warning, "message"),
                    object_field(warning, "related_object_id"),
                ]
            )
        )
    return lines


def render_case_structurer_result_tables(corrected_result: Any) -> list[str]:
    lines = [
        "## Case Structurer Results",
        "",
    ]
    table_sections = [
        render_stage_context_table(object_field(corrected_result, "stage_context")),
        render_clinical_sections_table(
            object_list_field(corrected_result, "clinical_sections")
        ),
        render_structured_items_table(
            object_list_field(corrected_result, "structured_items")
        ),
        render_structuring_warnings_table(
            object_list_field(corrected_result, "structuring_warnings")
        ),
    ]

    for table_section in table_sections:
        lines.extend(table_section)
        lines.append("")

    return lines


def render_clinical_attributes_table(attributes: list[Any]) -> list[str]:
    lines = [
        "## Clinical Attributes",
        "",
        "| attribute_id | source_item_id | attribute_role | attribute_scope | span_text | applies_to_text | context_text | normalized_value | normalized_unit | normalized_text | extraction_confidence | source_span_id |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not attributes:
        lines.append(empty_markdown_row(12, "No clinical attributes produced."))
        return lines

    for attribute in attributes:
        source_span = object_field(attribute, "source_span")
        lines.append(
            markdown_row(
                [
                    object_field(attribute, "attribute_id"),
                    object_field(attribute, "source_item_id"),
                    object_field(attribute, "attribute_role"),
                    object_field(attribute, "attribute_scope"),
                    object_field(attribute, "span_text"),
                    object_field(attribute, "applies_to_text"),
                    object_field(attribute, "context_text"),
                    object_field(attribute, "normalized_value"),
                    object_field(attribute, "normalized_unit"),
                    object_field(attribute, "normalized_text"),
                    object_field(attribute, "extraction_confidence"),
                    object_field(source_span, "span_id"),
                ]
            )
        )
    return lines


def render_round_markdown_summary(
    *,
    round_summary: dict[str, Any],
    corrected_result: Any,
    attribute_result: Any,
    atomization_result: Any,
    attribute_validation_report: Any,
    validation_report: Any,
) -> str:
    issues = object_list_field(validation_report, "issues")
    attribute_issues = object_list_field(attribute_validation_report, "issues")
    attributes = object_list_field(attribute_result, "clinical_attributes")
    atoms = object_list_field(atomization_result, "evidence_atoms")

    lines: list[str] = [
        f"# Phase 1 Trace Round {round_summary['round_index']:03d}",
        "",
        f"- Selected file: {round_summary['selected_file']}",
        f"- case_id: {round_summary['case_id']}",
        f"- input_id: {round_summary['input_id']}",
        f"- parent_input_id: {round_summary['parent_input_id']}",
        f"- input_order: {round_summary['input_order']}",
        f"- case_structuring_result_id: {round_summary['case_structuring_result_id']}",
        f"- attribute_extraction_result_id: {round_summary['attribute_extraction_result_id']}",
        f"- atomization_result_id: {round_summary['atomization_result_id']}",
        f"- case_structurer_duration: {format_duration(round_summary['case_structurer_duration_seconds'])}",
        f"- attribute_extractor_duration: {format_duration(round_summary['attribute_extraction_duration_seconds'])}",
        f"- evidence_atomizer_duration: {format_duration(round_summary['evidence_atomizer_duration_seconds'])}",
        f"- round_duration: {format_duration(round_summary['round_duration_seconds'])}",
        "",
        "## Structuring Summary",
        "",
        f"- ready_for_attribute_extraction: {round_summary['ready_for_attribute_extraction']}",
        f"- clinical_sections: {round_summary['number_of_clinical_sections']}",
        f"- structured_items: {round_summary['number_of_structured_items']}",
        "",
    ]

    lines.extend(render_case_structurer_result_tables(corrected_result))

    lines.extend(
        [
            "## Attribute Extraction Summary",
            "",
            f"- attribute_extraction_result_id: {round_summary['attribute_extraction_result_id']}",
            f"- clinical_attributes: {round_summary['number_of_clinical_attributes']}",
            f"- ready_for_evidence_atomization: {round_summary['ready_for_evidence_atomization']}",
            f"- validation_accepted: {round_summary['attribute_extraction_validation_accepted']}",
            "",
            "## Attribute Extractor Validation Issues",
            "",
        ]
    )

    if attribute_issues:
        lines.extend(
            [
                "| severity | code | message | related_item_id | related_attribute_id |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for issue in attribute_issues:
            lines.append(
                markdown_row(
                    [
                        object_field(issue, "severity"),
                        object_field(issue, "code"),
                        object_field(issue, "message"),
                        object_field(issue, "related_item_id"),
                        object_field(issue, "related_attribute_id"),
                    ]
                )
            )
    else:
        lines.append("No validation issues.")

    lines.append("")
    lines.extend(render_clinical_attributes_table(attributes))
    lines.append("")

    lines.extend(
        [
            "## Atomization Summary",
            "",
            f"- atomization_result_id: {round_summary['atomization_result_id']}",
            f"- evidence_atoms: {round_summary['number_of_evidence_atoms']}",
            f"- item_to_evidence_links: {round_summary['number_of_item_to_evidence_links']}",
            f"- deferred_items: {round_summary['number_of_deferred_items']}",
            f"- atomization_warnings: {round_summary['number_of_atomization_warnings']}",
            f"- validation_accepted: {round_summary['evidence_atomization_validation_accepted']}",
            "",
            "## Evidence Atomizer Validation Issues",
            "",
        ]
    )

    if issues:
        lines.extend(
            [
                "| severity | code | message | related_item_id | related_attribute_id | related_evidence_id | related_span_id |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for issue in issues:
            lines.append(
                markdown_row(
                    [
                        object_field(issue, "severity"),
                        object_field(issue, "code"),
                        object_field(issue, "message"),
                        object_field(issue, "related_item_id"),
                        object_field(issue, "related_attribute_id"),
                        object_field(issue, "related_evidence_id"),
                        object_field(issue, "related_span_id"),
                    ]
                )
            )
    else:
        lines.append("No validation issues.")

    lines.extend(
        [
            "",
            "## Evidence Atoms",
            "",
            "| evidence_id | evidence_type | clinical_domain | statement | normalized_label | assertion_status | certainty | temporality | source_item_ids | source_attribute_ids | source_span_ids | source_text |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for atom in atoms:
        lines.append(
            markdown_row(
                [
                    object_field(atom, "evidence_id"),
                    object_field(atom, "evidence_type"),
                    object_field(atom, "clinical_domain"),
                    object_field(atom, "statement"),
                    object_field(atom, "normalized_label"),
                    object_field(atom, "assertion_status"),
                    object_field(atom, "certainty"),
                    object_field(atom, "temporality"),
                    join_markdown_values(object_field(atom, "source_item_ids", [])),
                    join_markdown_values(
                        object_field(atom, "source_attribute_ids", [])
                    ),
                    join_markdown_values(object_field(atom, "source_span_ids", [])),
                    object_field(atom, "source_text"),
                ]
            )
        )

    if not atoms:
        lines.append(empty_markdown_row(12, "No evidence atoms produced."))

    lines.extend(["", "## Boundary Note", "", MULTI_ROUND_NOTE, ""])
    return "\n".join(lines)


def build_round_summary(
    *,
    round_index: int,
    selected_file: Path,
    corrected_result: Any,
    attribute_result: Any,
    atomization_result: Any,
    attribute_validation_report: Any,
    validation_report: Any,
    case_structurer_duration_seconds: float,
    attribute_extraction_duration_seconds: float,
    evidence_atomizer_duration_seconds: float,
    round_duration_seconds: float,
) -> dict[str, Any]:
    return {
        "round_index": round_index,
        "selected_file": display_path(selected_file),
        "case_id": corrected_result.input.case_id,
        "input_id": corrected_result.input.input_id,
        "parent_input_id": corrected_result.input.parent_input_id,
        "input_order": corrected_result.input.input_order,
        "case_structuring_result_id": corrected_result.case_structuring_result_id,
        "ready_for_attribute_extraction": (
            corrected_result.ready_for_attribute_extraction
        ),
        "ready_for_evidence_atomization": (
            attribute_result.ready_for_evidence_atomization
        ),
        "number_of_clinical_sections": len(corrected_result.clinical_sections),
        "number_of_structured_items": len(corrected_result.structured_items),
        "attribute_extraction_result_id": (
            attribute_result.attribute_extraction_result_id
        ),
        "number_of_clinical_attributes": len(
            attribute_result.clinical_attributes
        ),
        "number_of_attribute_extraction_warnings": len(
            attribute_result.extraction_warnings
        ),
        "attribute_extraction_validation_accepted": (
            attribute_validation_report.accepted
        ),
        "attribute_extraction_validation_issue_counts_by_severity": (
            issue_counts_by_severity(attribute_validation_report)
        ),
        "attribute_extraction_validation_issue_counts_by_code": (
            issue_counts_by_code(attribute_validation_report)
        ),
        "atomization_result_id": atomization_result.atomization_result_id,
        "number_of_evidence_atoms": len(atomization_result.evidence_atoms),
        "number_of_item_to_evidence_links": len(
            atomization_result.item_to_evidence_links
        ),
        "number_of_deferred_items": len(atomization_result.deferred_items),
        "number_of_atomization_warnings": len(atomization_result.atomization_warnings),
        "evidence_atomization_validation_accepted": validation_report.accepted,
        "evidence_atomization_validation_issue_counts_by_severity": (
            issue_counts_by_severity(validation_report)
        ),
        "evidence_atomization_validation_issue_counts_by_code": (
            issue_counts_by_code(validation_report)
        ),
        "case_structurer_duration_seconds": round(
            case_structurer_duration_seconds,
            3,
        ),
        "attribute_extraction_duration_seconds": round(
            attribute_extraction_duration_seconds,
            3,
        ),
        "evidence_atomizer_duration_seconds": round(
            evidence_atomizer_duration_seconds,
            3,
        ),
        "round_duration_seconds": round(round_duration_seconds, 3),
    }


def build_manifest(
    *,
    case_id: str,
    created_at: str,
    result_root: Path,
    round_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "created_at": created_at,
        "total_rounds": len(round_summaries),
        "result_root": str(result_root),
        "rounds": [
            {
                "round_index": summary["round_index"],
                "selected_file": summary["selected_file"],
                "input_id": summary["input_id"],
                "parent_input_id": summary["parent_input_id"],
                "case_structuring_result_id": summary[
                    "case_structuring_result_id"
                ],
                "attribute_extraction_result_id": summary[
                    "attribute_extraction_result_id"
                ],
                "atomization_result_id": summary["atomization_result_id"],
                "clinical_attribute_count": summary[
                    "number_of_clinical_attributes"
                ],
                "evidence_atom_count": summary["number_of_evidence_atoms"],
                "validation_accepted": summary[
                    "evidence_atomization_validation_accepted"
                ],
            }
            for summary in round_summaries
        ],
    }


def build_case_level_summary(
    *,
    case_id: str,
    round_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "total_rounds": len(round_summaries),
        "total_evidence_atoms_across_rounds": sum(
            summary["number_of_evidence_atoms"] for summary in round_summaries
        ),
        "total_clinical_attributes_across_rounds": sum(
            summary["number_of_clinical_attributes"] for summary in round_summaries
        ),
        "total_deferred_items_across_rounds": sum(
            summary["number_of_deferred_items"] for summary in round_summaries
        ),
        "total_atomization_warnings_across_rounds": sum(
            summary["number_of_atomization_warnings"] for summary in round_summaries
        ),
        "all_round_input_ids": [
            summary["input_id"] for summary in round_summaries
        ],
        "all_case_structuring_result_ids": [
            summary["case_structuring_result_id"] for summary in round_summaries
        ],
        "all_attribute_extraction_result_ids": [
            summary["attribute_extraction_result_id"] for summary in round_summaries
        ],
        "all_atomization_result_ids": [
            summary["atomization_result_id"] for summary in round_summaries
        ],
        "any_round_rejected_by_validator": any(
            not summary["evidence_atomization_validation_accepted"]
            for summary in round_summaries
        ),
    }


def write_case_level_outputs(
    *,
    result_root: Path,
    case_id: str,
    created_at: str,
    round_summaries: list[dict[str, Any]],
) -> None:
    write_json(
        result_root / "manifest.json",
        build_manifest(
            case_id=case_id,
            created_at=created_at,
            result_root=result_root,
            round_summaries=round_summaries,
        ),
    )
    write_json(
        result_root / "case_level_summary.json",
        build_case_level_summary(
            case_id=case_id,
            round_summaries=round_summaries,
        ),
    )


def print_round_console_summary(
    *,
    summary: dict[str, Any],
    attribute_validation_report: Any,
    validation_report: Any,
    round_dir: Path,
) -> None:
    attribute_codes = issue_codes(attribute_validation_report)
    codes = issue_codes(validation_report)
    print("\nRound trace summary")
    print(f"- Round number: {summary['round_index']}")
    print(f"- Selected file: {summary['selected_file']}")
    print(f"- case_id: {summary['case_id']}")
    print(f"- input_id: {summary['input_id']}")
    print(f"- parent_input_id: {summary['parent_input_id']}")
    print(
        "- case_structuring_result_id: "
        f"{summary['case_structuring_result_id']}"
    )
    print(f"- structured_items: {summary['number_of_structured_items']}")
    print(
        "- attribute_extraction_result_id: "
        f"{summary['attribute_extraction_result_id']}"
    )
    print(f"- clinical_attributes: {summary['number_of_clinical_attributes']}")
    print(f"- atomization_result_id: {summary['atomization_result_id']}")
    print(f"- evidence_atoms: {summary['number_of_evidence_atoms']}")
    print(f"- deferred_items: {summary['number_of_deferred_items']}")
    print(f"- atomization_warnings: {summary['number_of_atomization_warnings']}")
    print(
        "- case structurer duration: "
        f"{format_duration(summary['case_structurer_duration_seconds'])}"
    )
    print(
        "- attribute extractor duration: "
        f"{format_duration(summary['attribute_extraction_duration_seconds'])}"
    )
    print(
        "- evidence atomizer duration: "
        f"{format_duration(summary['evidence_atomizer_duration_seconds'])}"
    )
    print(
        "- total round duration: "
        f"{format_duration(summary['round_duration_seconds'])}"
    )
    print(
        "- attribute validation accepted: "
        f"{summary['attribute_extraction_validation_accepted']}"
    )
    print(f"- attribute validation issue codes: {attribute_codes if attribute_codes else 'none'}")
    print(
        "- evidence validation accepted: "
        f"{summary['evidence_atomization_validation_accepted']}"
    )
    print(f"- evidence validation issue codes: {codes if codes else 'none'}")
    print(f"- round output directory: {round_dir}")
    if not summary["attribute_extraction_validation_accepted"]:
        print("Attribute Extractor validation was rejected; saved output anyway.")
    if not summary["evidence_atomization_validation_accepted"]:
        print("Evidence Atomizer validation was rejected; saved output anyway.")


def save_round_inputs(
    *,
    round_dir: Path,
    raw_text: str,
    selected_file_payload: dict[str, Any],
) -> None:
    write_text(round_dir / "raw_input.txt", raw_text)
    write_json(round_dir / "selected_file.json", selected_file_payload)


def initialize_agents() -> tuple[Any, Any, Any]:
    (
        CaseStructurerAgent,
        AttributeExtractorAgent,
        EvidenceAtomizerAgent,
        ChatAnywhereClient,
    ) = load_runtime_components()
    llm_client = ChatAnywhereClient()
    return (
        CaseStructurerAgent(llm_client=llm_client),
        AttributeExtractorAgent(llm_client=llm_client),
        EvidenceAtomizerAgent(llm_client=llm_client),
    )


def run_case_structurer_round(
    *,
    raw_text: str,
    round_dir: Path,
    case_structurer_agent: Any,
    case_id: str | None,
    input_order: int,
    parent_input_id: str | None,
) -> tuple[Any, Any, float]:
    timer = LiveTimer("Case Structurer")
    try:
        with timer:
            case_bundle = case_structurer_agent.run_with_validation(
                raw_text=raw_text,
                case_id=case_id,
                input_order=input_order,
                parent_input_id=parent_input_id,
            )
    except Exception as exc:
        write_json(round_dir / "error.json", exception_payload("case_structurer", exc))
        print(
            "ERROR: Case Structurer failed after "
            f"{format_duration(timer.elapsed_seconds)} "
            f"({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        raise

    duration = timer.elapsed_seconds
    corrected_result = case_bundle.corrected_result
    write_json(
        round_dir / "case_structuring_corrected.json",
        corrected_result.model_dump(mode="json"),
    )
    write_json(
        round_dir / "case_structuring_validation_bundle.json",
        safe_validation_bundle_payload(case_bundle),
    )
    return case_bundle, corrected_result, duration


def run_attribute_extractor_round(
    *,
    corrected_result: Any,
    round_dir: Path,
    attribute_extractor_agent: Any,
) -> tuple[Any, Any, float]:
    timer = LiveTimer("Attribute Extractor")
    try:
        with timer:
            attribute_bundle = attribute_extractor_agent.run_with_validation(
                corrected_result
            )
    except Exception as exc:
        write_json(
            round_dir / "error.json",
            exception_payload("attribute_extractor", exc),
        )
        print(
            "ERROR: Attribute Extractor failed after "
            f"{format_duration(timer.elapsed_seconds)} "
            f"({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        raise

    duration = timer.elapsed_seconds
    attribute_result = attribute_bundle.attribute_extraction_result
    validation_report = attribute_bundle.validation_report

    write_json(
        round_dir / "attribute_extraction_result.json",
        attribute_result.model_dump(mode="json"),
    )
    write_json(
        round_dir / "clinical_attributes.json",
        [
            attribute.model_dump(mode="json")
            for attribute in attribute_result.clinical_attributes
        ],
    )
    write_json(
        round_dir / "attribute_extraction_validation_report.json",
        validation_report.model_dump(mode="json"),
    )
    return attribute_result, validation_report, duration


def run_evidence_atomizer_round(
    *,
    corrected_result: Any,
    attribute_result: Any,
    round_dir: Path,
    evidence_atomizer_agent: Any,
) -> tuple[Any, Any, float]:
    timer = LiveTimer("Evidence Atomizer")
    try:
        with timer:
            atomization_bundle = evidence_atomizer_agent.run_with_validation(
                corrected_result,
                attribute_result,
            )
    except Exception as exc:
        write_json(round_dir / "error.json", exception_payload("evidence_atomizer", exc))
        print(
            "ERROR: Evidence Atomizer failed after "
            f"{format_duration(timer.elapsed_seconds)} "
            f"({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        raise

    duration = timer.elapsed_seconds
    atomization_result = atomization_bundle.atomization_result
    validation_report = atomization_bundle.validation_report

    write_json(
        round_dir / "evidence_atomization_result.json",
        atomization_result.model_dump(mode="json"),
    )
    write_json(
        round_dir / "evidence_atomization_validation_report.json",
        validation_report.model_dump(mode="json"),
    )
    if getattr(atomization_bundle, "clinical_assertion_resolution", None) is not None:
        clinical_assertion_resolution = atomization_bundle.clinical_assertion_resolution
        write_json(
            round_dir / "clinical_object_assertions.json",
            [
                assertion.model_dump(mode="json")
                for assertion in clinical_assertion_resolution.clinical_object_assertions
            ],
        )
        write_json(
            round_dir / "clinical_assertion_warnings.json",
            [
                warning.model_dump(mode="json")
                for warning in clinical_assertion_resolution.assertion_warnings
            ],
        )
    write_json(
        round_dir / "evidence_atoms.json",
        [atom.model_dump(mode="json") for atom in atomization_result.evidence_atoms],
    )
    return atomization_result, validation_report, duration


def write_round_summaries(
    *,
    round_index: int,
    selected_file: Path,
    round_dir: Path,
    corrected_result: Any,
    attribute_result: Any,
    atomization_result: Any,
    attribute_validation_report: Any,
    validation_report: Any,
    case_structurer_duration_seconds: float,
    attribute_extraction_duration_seconds: float,
    evidence_atomizer_duration_seconds: float,
    round_duration_seconds: float,
) -> dict[str, Any]:
    summary = build_round_summary(
        round_index=round_index,
        selected_file=selected_file,
        corrected_result=corrected_result,
        attribute_result=attribute_result,
        atomization_result=atomization_result,
        attribute_validation_report=attribute_validation_report,
        validation_report=validation_report,
        case_structurer_duration_seconds=case_structurer_duration_seconds,
        attribute_extraction_duration_seconds=(
            attribute_extraction_duration_seconds
        ),
        evidence_atomizer_duration_seconds=evidence_atomizer_duration_seconds,
        round_duration_seconds=round_duration_seconds,
    )
    write_json(round_dir / "round_summary.json", summary)
    write_text(
        round_dir / "trace_summary.md",
        render_round_markdown_summary(
            round_summary=summary,
            corrected_result=corrected_result,
            attribute_result=attribute_result,
            atomization_result=atomization_result,
            attribute_validation_report=attribute_validation_report,
            validation_report=validation_report,
        ),
    )
    return summary


def main() -> int:
    data_dir = DEFAULT_DATA_DIR.resolve()
    files = find_data_files(data_dir)
    if not data_dir.exists():
        print(f"No data directory found: {data_dir}")
        return 1
    if not files:
        print(
            "No usable data files found. Expected readable .txt, .md, .json, "
            f"or .csv files under {data_dir}."
        )
        return 1

    print(
        "Phase 1 interactive trace: "
        "Case Structurer -> Attribute Extractor -> Evidence Atomizer"
    )
    print(MULTI_ROUND_NOTE)

    case_id: str | None = None
    previous_input_id: str | None = None
    case_structurer_agent: Any | None = None
    attribute_extractor_agent: Any | None = None
    evidence_atomizer_agent: Any | None = None
    result_root: Path | None = None
    timestamp = make_timestamp()
    created_at = utc_now_iso()
    round_summaries: list[dict[str, Any]] = []
    round_index = 1

    while True:
        files = find_data_files(data_dir)
        if not files:
            print(
                "No usable data files found. Expected readable .txt, .md, .json, "
                f"or .csv files under {data_dir}."
            )
            return 1

        try:
            selected_file = choose_file(files)
        except KeyboardInterrupt:
            print("\nNo file selected. Exiting.")
            if result_root is not None and round_summaries and case_id is not None:
                write_case_level_outputs(
                    result_root=result_root,
                    case_id=case_id,
                    created_at=created_at,
                    round_summaries=round_summaries,
                )
                print(f"Result directory: {result_root}")
            return 0

        input_order = round_index
        parent_input_id = previous_input_id if round_index > 1 else None
        if result_root is None:
            result_root = DEFAULT_RESULT_ROOT / f"pending_{timestamp}"
            result_root.mkdir(parents=True, exist_ok=False)
        round_dir = make_round_dir(result_root, round_index)
        selected_file_payload = make_selected_file_payload(
            selected_file=selected_file,
            round_index=round_index,
            input_order=input_order,
            parent_input_id=parent_input_id,
            case_id=case_id,
        )

        try:
            raw_text = read_utf8_text(selected_file)
        except Exception as exc:
            save_round_inputs(
                round_dir=round_dir,
                raw_text="",
                selected_file_payload=selected_file_payload,
            )
            write_json(round_dir / "error.json", exception_payload("read_input", exc))
            print(
                f"ERROR: Failed to read selected file as UTF-8 "
                f"({type(exc).__name__}): {exc}",
                file=sys.stderr,
            )
            return 1

        save_round_inputs(
            round_dir=round_dir,
            raw_text=raw_text,
            selected_file_payload=selected_file_payload,
        )

        if (
            case_structurer_agent is None
            or attribute_extractor_agent is None
            or evidence_atomizer_agent is None
        ):
            try:
                (
                    case_structurer_agent,
                    attribute_extractor_agent,
                    evidence_atomizer_agent,
                ) = initialize_agents()
            except Exception as exc:
                write_json(
                    round_dir / "error.json",
                    exception_payload("startup", exc),
                )
                print(
                    "ERROR: Unable to initialize real LLM pipeline. "
                    "Check CHATANYWHERE_API_KEY and configs/agents.yaml.",
                    file=sys.stderr,
                )
                print(f"Detail ({type(exc).__name__}): {exc}", file=sys.stderr)
                print(f"Partial trace saved at: {round_dir}", file=sys.stderr)
                return 2

        print(
            f"\nRunning round {round_index}: {display_path(selected_file)} "
            f"(input_order={input_order}, parent_input_id={parent_input_id})"
        )
        round_start = perf_counter()

        try:
            (
                _case_bundle,
                corrected_result,
                case_structurer_duration_seconds,
            ) = run_case_structurer_round(
                raw_text=raw_text,
                round_dir=round_dir,
                case_structurer_agent=case_structurer_agent,
                case_id=case_id,
                input_order=input_order,
                parent_input_id=parent_input_id,
            )
        except Exception:
            print(f"Partial round trace saved at: {round_dir}", file=sys.stderr)
            return 1

        if case_id is None:
            case_id = corrected_result.input.case_id
            if result_root is None:
                raise RuntimeError("Result root was not initialized.")
            result_root = maybe_promote_result_root(result_root, case_id, timestamp)
            round_dir = result_root / f"round_{round_index:03d}"

        try:
            (
                attribute_result,
                attribute_validation_report,
                attribute_extraction_duration_seconds,
            ) = run_attribute_extractor_round(
                corrected_result=corrected_result,
                round_dir=round_dir,
                attribute_extractor_agent=attribute_extractor_agent,
            )
        except Exception:
            print(f"Partial round trace saved at: {round_dir}", file=sys.stderr)
            return 1

        try:
            (
                atomization_result,
                validation_report,
                evidence_atomizer_duration_seconds,
            ) = run_evidence_atomizer_round(
                corrected_result=corrected_result,
                attribute_result=attribute_result,
                round_dir=round_dir,
                evidence_atomizer_agent=evidence_atomizer_agent,
            )
        except Exception:
            print(f"Partial round trace saved at: {round_dir}", file=sys.stderr)
            return 1

        round_duration_seconds = perf_counter() - round_start
        print(
            f"Round {round_index} completed in "
            f"{format_duration(round_duration_seconds)}."
        )

        summary = write_round_summaries(
            round_index=round_index,
            selected_file=selected_file,
            round_dir=round_dir,
            corrected_result=corrected_result,
            attribute_result=attribute_result,
            atomization_result=atomization_result,
            attribute_validation_report=attribute_validation_report,
            validation_report=validation_report,
            case_structurer_duration_seconds=case_structurer_duration_seconds,
            attribute_extraction_duration_seconds=(
                attribute_extraction_duration_seconds
            ),
            evidence_atomizer_duration_seconds=evidence_atomizer_duration_seconds,
            round_duration_seconds=round_duration_seconds,
        )
        previous_input_id = corrected_result.input.input_id
        round_summaries.append(summary)
        write_case_level_outputs(
            result_root=result_root,
            case_id=case_id,
            created_at=created_at,
            round_summaries=round_summaries,
        )
        print_round_console_summary(
            summary=summary,
            attribute_validation_report=attribute_validation_report,
            validation_report=validation_report,
            round_dir=round_dir,
        )

        if not ask_continue():
            break
        round_index += 1

    if case_id is None:
        print("No rounds were executed.")
        return 1
    if result_root is None:
        raise RuntimeError("Result root was not initialized.")

    write_case_level_outputs(
        result_root=result_root,
        case_id=case_id,
        created_at=created_at,
        round_summaries=round_summaries,
    )
    print("\nDone.")
    print(f"Final case_id: {case_id}")
    print(f"Total rounds: {len(round_summaries)}")
    print(f"Result directory: {result_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
