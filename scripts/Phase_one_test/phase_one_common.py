from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from html import escape
import json
from pathlib import Path
from typing import Any


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)} min {remainder:.1f} s"


def short_id(value: Any, keep: int = 8) -> str:
    text = str(value or "").strip()
    if len(text) <= keep + 4:
        return text
    return text[-keep:]


def enum_text(value: Any) -> str:
    if value is None:
        return ""
    return str(getattr(value, "value", value))


def obj_field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def obj_list(obj: Any, name: str) -> list[Any]:
    value = obj_field(obj, name, [])
    if value is None:
        return []
    return list(value)


def model_to_jsonable(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
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
    path.write_text(
        json.dumps(model_to_jsonable(data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def compact(text: Any, limit: int = 150) -> str:
    value = " ".join(enum_text(text).replace("\n", " ").replace("\r", " ").split())
    if len(value) <= limit:
        return value
    return f"{value[: limit - 1]}..."


def index_by(items: list[Any], key: str) -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = {}
    for item in items:
        value = enum_text(obj_field(item, key))
        grouped.setdefault(value, []).append(item)
    return grouped


def h(value: Any) -> str:
    return escape(enum_text(value), quote=True)


def badge(value: Any, kind: str = "") -> str:
    text = h(value)
    cls = f"badge {kind}".strip()
    return f'<span class="{cls}">{text}</span>'


def source_text_for_item(item: Any) -> str:
    spans = obj_list(item, "source_spans")
    text = "\n".join(enum_text(obj_field(span, "quoted_text")) for span in spans)
    return text or enum_text(obj_field(item, "label"))


def warning_counts(warnings: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for warning in warnings:
        code = enum_text(obj_field(warning, "code", "unknown"))
        counts[code] = counts.get(code, 0) + 1
    return dict(sorted(counts.items()))
