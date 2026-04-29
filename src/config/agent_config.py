from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AgentLLMConfig:
    provider: str
    model: str
    temperature: float
    max_tokens: int
    prompt_path: str
    response_format: str | None = None


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
        return AgentLLMConfig(
            provider=str(raw_config["provider"]),
            model=str(raw_config["model"]),
            temperature=float(raw_config["temperature"]),
            max_tokens=int(raw_config["max_tokens"]),
            prompt_path=str(raw_config["prompt_path"]),
            response_format=(
                str(raw_config["response_format"])
                if raw_config.get("response_format") is not None
                else None
            ),
        )
    except KeyError as exc:
        raise ValueError(
            f"Missing required key in agent config '{agent_name}': {exc.args[0]}"
        ) from exc
