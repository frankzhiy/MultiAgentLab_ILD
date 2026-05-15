from __future__ import annotations

from typing import Any

from src.config.settings import Settings


class ChatAnywhereClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.client: Any = _build_openai_client(self.settings)

    def generate_json(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        response_format: str | None = "json_object",
    ) -> str:
        request_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            request_kwargs["response_format"] = {"type": response_format}

        response = self.client.chat.completions.create(**request_kwargs)

        content = response.choices[0].message.content
        if content is None or not content.strip():
            raise RuntimeError("LLM returned empty content.")

        return content


def _build_openai_client(settings: Settings) -> Any:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "ChatAnywhereClient requires the openai package. Install project "
            "dependencies before running real LLM pipelines."
        ) from exc

    return OpenAI(
        api_key=settings.chatanywhere_api_key,
        base_url=settings.chatanywhere_base_url,
    )
