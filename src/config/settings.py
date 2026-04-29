from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional import at runtime
    load_dotenv = None


DEFAULT_CHATANYWHERE_BASE_URL = "https://api.chatanywhere.tech/v1"


@dataclass(frozen=True)
class Settings:
    chatanywhere_api_key: str
    chatanywhere_base_url: str = DEFAULT_CHATANYWHERE_BASE_URL

    @classmethod
    def from_env(cls) -> "Settings":
        if load_dotenv is not None:
            load_dotenv()

        api_key = os.getenv("CHATANYWHERE_API_KEY", "").strip()
        base_url = os.getenv(
            "CHATANYWHERE_BASE_URL",
            DEFAULT_CHATANYWHERE_BASE_URL,
        ).strip()

        if not api_key:
            raise ValueError(
                "CHATANYWHERE_API_KEY is required. "
                "Set it in your environment or in a .env file."
            )

        if not base_url:
            base_url = DEFAULT_CHATANYWHERE_BASE_URL

        return cls(
            chatanywhere_api_key=api_key,
            chatanywhere_base_url=base_url,
        )
