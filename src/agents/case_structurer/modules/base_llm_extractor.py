from __future__ import annotations

import json
from pathlib import Path
from enum import StrEnum
from typing import Any

from src.config.agent_config import AgentLLMConfig, load_agent_config
from src.llm.chatanywhere_client import ChatAnywhereClient
from src.schemas.case_structurer.raw_text_input import RawTextInput


class BaseLLMExtractor:
    """Shared ChatAnywhere JSON generation helper for pipeline extractors."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "case_structurer",
    ) -> None:
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.config: AgentLLMConfig = load_agent_config(agent_name)

    def load_prompt(self, prompt_path: str) -> str:
        repo_root = Path(__file__).resolve().parents[4]
        resolved_path = repo_root / prompt_path
        return resolved_path.read_text(encoding="utf-8")

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
        response_format: str | None = "json_object",
    ) -> str:
        prompt_text = self.load_prompt(prompt_path)
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

    @classmethod
    def prepare_source_spans(
        cls,
        raw_input: RawTextInput,
        payload: dict[str, Any],
        default_quoted_text: str,
        span_prefix: str,
    ) -> list[dict[str, Any]]:
        raw_spans = payload.get("source_spans")
        if raw_spans is None:
            raw_spans = payload.get("source_span")
        if raw_spans is None:
            raw_spans = payload.get("spans")

        if isinstance(raw_spans, dict):
            raw_span_items: list[Any] = [raw_spans]
        elif isinstance(raw_spans, list):
            raw_span_items = raw_spans
        else:
            raw_span_items = []

        spans: list[dict[str, Any]] = []
        for index, raw_span in enumerate(raw_span_items, start=1):
            if isinstance(raw_span, dict):
                quoted_text = cls.first_text(
                    raw_span,
                    ("quoted_text", "source_text", "text", "fragment"),
                )
                span_id = raw_span.get("span_id") or f"{span_prefix}_{index:03d}"
                char_start = raw_span.get("char_start")
                char_end = raw_span.get("char_end")
            else:
                quoted_text = str(raw_span).strip()
                span_id = f"{span_prefix}_{index:03d}"
                char_start = None
                char_end = None

            if not quoted_text:
                quoted_text = default_quoted_text

            if not isinstance(char_start, int) or not isinstance(char_end, int):
                char_start = None
                char_end = None
            elif char_end <= char_start:
                char_start = None
                char_end = None

            spans.append(
                {
                    "span_id": span_id,
                    "input_id": raw_input.input_id,
                    "quoted_text": quoted_text,
                    "char_start": char_start,
                    "char_end": char_end,
                }
            )

        if not spans:
            spans.append(
                {
                    "span_id": f"{span_prefix}_001",
                    "input_id": raw_input.input_id,
                    "quoted_text": default_quoted_text,
                    "char_start": None,
                    "char_end": None,
                }
            )

        return spans
