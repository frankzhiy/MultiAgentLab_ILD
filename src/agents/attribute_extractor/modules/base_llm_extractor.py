from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

from src.agents.case_structurer.prompting.template_renderer import (
    PromptTemplateRenderer,
)
from src.config.agent_config import AgentLLMConfig, load_agent_config
from src.llm.chatanywhere_client import ChatAnywhereClient


class BaseLLMExtractor:
    """Shared ChatAnywhere JSON generation helper for Attribute Extractor."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient,
        agent_name: str = "attribute_extractor",
    ) -> None:
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.config: AgentLLMConfig = load_agent_config(agent_name)
        self.prompt_renderer = PromptTemplateRenderer()

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
    def coerce_optional_text(value: Any) -> str | None:
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
