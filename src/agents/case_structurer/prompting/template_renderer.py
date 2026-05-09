from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, StrictUndefined
from jinja2.exceptions import UndefinedError


class PromptTemplateRenderer:
    """Render Jinja2 prompt templates from repo-relative or absolute paths."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root.resolve() if repo_root else self._find_repo_root()
        self.environment = Environment(
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )

    def render_file(
        self,
        template_path: str | Path,
        variables: dict[str, Any],
    ) -> str:
        resolved_path = self._resolve_template_path(template_path)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {resolved_path}")

        template_text = resolved_path.read_text(encoding="utf-8")
        template = self.environment.from_string(template_text)
        try:
            return template.render(**variables)
        except UndefinedError as exc:
            missing_name = self._missing_variable_name(str(exc))
            raise ValueError(
                f"Missing template variable '{missing_name}' while rendering "
                f"{resolved_path}."
            ) from exc

    def _resolve_template_path(self, template_path: str | Path) -> Path:
        path = Path(template_path)
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root / path).resolve()

    @staticmethod
    def _missing_variable_name(error_message: str) -> str:
        match = re.search(r"'([^']+)' is undefined", error_message)
        if match:
            return match.group(1)
        return error_message

    @staticmethod
    def _find_repo_root() -> Path:
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                return parent
        return current.parents[4]
