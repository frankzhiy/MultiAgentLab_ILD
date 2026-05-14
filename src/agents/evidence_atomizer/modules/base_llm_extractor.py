from __future__ import annotations

import json
import re
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, StrictUndefined
from jinja2.exceptions import UndefinedError

from src.config.agent_config import AgentLLMConfig, load_agent_config

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient


class BaseLLMExtractor:
    """Evidence Atomizer-specific ChatAnywhere JSON generation helper."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "evidence_atomizer",
    ) -> None:
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.config: AgentLLMConfig = load_agent_config(agent_name)
        self.prompt_renderer = _PromptTemplateRenderer()

    def prompt_path(self, prompt_name: str) -> str:
        try:
            return self.config.prompts[prompt_name]
        except KeyError as exc:
            available = ", ".join(sorted(self.config.prompts)) or "(none)"
            raise ValueError(
                f"Prompt '{prompt_name}' is not configured for agent "
                f"'{self.agent_name}'. Available prompts: {available}."
            ) from exc

    def generate_json(
        self,
        prompt_path: str,
        user_payload: dict[str, Any],
        instruction: str,
        template_vars: dict[str, Any] | None = None,
        response_format: str | None = "json_object",
    ) -> str:
        prompt_text = self.prompt_renderer.render_file(
            prompt_path,
            template_vars or {},
        )
        payload_text = json.dumps(
            user_payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        user_message = f"{instruction}\n\nInput JSON:\n{payload_text}"

        return self.llm_client.generate_json(
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": user_message},
            ],
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format=response_format,
        )

    @staticmethod
    def parse_json_content(content: str) -> Any:
        stripped = content.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        return json.loads(stripped)

    @staticmethod
    def extract_array_payload(payload: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = None
            for key in keys:
                candidate = payload.get(key)
                if isinstance(candidate, list):
                    items = candidate
                    break
            if items is None:
                raise ValueError(
                    "Expected a JSON array or an object containing one of: "
                    f"{', '.join(keys)}."
                )
        else:
            raise ValueError("Expected a JSON array payload.")

        if not all(isinstance(item, dict) for item in items):
            raise ValueError("Expected every extracted array item to be a JSON object.")

        return items

    @staticmethod
    def first_text(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    def coerce_optional_text(value: Any) -> str | None:
        """Coerce LLM scalar output into an optional schema text field."""
        if value is None:
            return None
        if isinstance(value, StrEnum):
            value = value.value
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int | float):
            return str(value)
        return None

    @staticmethod
    def coerce_enum_value(
        value: Any,
        enum_type: type[StrEnum],
        default: str,
    ) -> str:
        allowed_values = {item.value for item in enum_type}
        if isinstance(value, StrEnum):
            value = value.value
        if isinstance(value, str) and value in allowed_values:
            return value
        return default


class _PromptTemplateRenderer:
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
