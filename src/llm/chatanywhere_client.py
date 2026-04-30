from __future__ import annotations

from openai import OpenAI

from src.config.settings import Settings


class ChatAnywhereClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.client = OpenAI(
            api_key=self.settings.chatanywhere_api_key,
            base_url=self.settings.chatanywhere_base_url,
        )

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
