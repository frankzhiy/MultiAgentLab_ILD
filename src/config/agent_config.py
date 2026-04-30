from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AgentLLMConfig:
    provider: str
    model: str
    temperature: float
    max_tokens: int
    prompt_path: str | None = None
    response_format: str | None = None
    prompts: dict[str, str] = field(default_factory=dict)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG_PATH = _REPO_ROOT / "configs" / "agents.yaml"


def load_agent_config(agent_name: str) -> AgentLLMConfig:
    with _DEFAULT_CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise ValueError(
            "Invalid agents config: top-level 'agents' mapping is required."
        )

    raw_config = agents.get(agent_name)
    if not isinstance(raw_config, dict):
        available_agents = ", ".join(sorted(agents.keys())) if agents else "(none)"
        raise ValueError(
            f"Agent config '{agent_name}' was not found in {_DEFAULT_CONFIG_PATH}. "
            f"Available agents: {available_agents}."
        )

    try:
        raw_prompts = raw_config.get("prompts") or {}
        if not isinstance(raw_prompts, dict):
            raise ValueError(
                f"Invalid 'prompts' value in agent config '{agent_name}': "
                "expected a mapping of prompt names to paths."
            )

        prompt_path = raw_config.get("prompt_path")
        prompts = {str(key): str(value) for key, value in raw_prompts.items()}

        if prompt_path is None and not prompts:
            raise ValueError(
                f"Agent config '{agent_name}' must define either "
                "'prompt_path' or 'prompts'."
            )

        return AgentLLMConfig(
            provider=str(raw_config["provider"]),
            model=str(raw_config["model"]),
            temperature=float(raw_config["temperature"]),
            max_tokens=int(raw_config["max_tokens"]),
            prompt_path=str(prompt_path) if prompt_path is not None else None,
            response_format=(
                str(raw_config["response_format"])
                if raw_config.get("response_format") is not None
                else None
            ),
            prompts=prompts,
        )
    except KeyError as exc:
        raise ValueError(
            f"Missing required key in agent config '{agent_name}': {exc.args[0]}"
        ) from exc
