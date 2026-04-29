from __future__ import annotations

from pathlib import Path

from src.config.agent_config import load_agent_config
from src.llm.chatanywhere_client import ChatAnywhereClient
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.utils.id_generator import generate_case_id


class CaseStructuringParseError(ValueError):
    """Raised when CaseStructuringResult parsing fails."""


class CaseStructurerAgent:
    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "case_structurer",
    ) -> None:
        self.llm_client = llm_client or ChatAnywhereClient()
        self.agent_name = agent_name

    def run(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> CaseStructuringResult:
        if case_id is None:
            case_id = generate_case_id()

        raw_input = RawTextInput(
            case_id=case_id,
            raw_text=raw_text,
            input_order=input_order,
            parent_input_id=parent_input_id,
        )

        config = load_agent_config(self.agent_name)
        prompt_text = self._load_prompt(config.prompt_path)

        user_message = (
            "RawTextInput JSON:\n"
            f"{raw_input.model_dump_json(indent=2)}\n\n"
            "Return exactly one JSON object that matches CaseStructuringResult."
        )

        content = self.llm_client.generate_json(
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": user_message},
            ],
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        try:
            return CaseStructuringResult.model_validate_json(content)
        except Exception as exc:
            raise CaseStructuringParseError(
                f"Failed to parse CaseStructuringResult: {exc}"
            ) from exc

    @staticmethod
    def _load_prompt(prompt_path: str) -> str:
        repo_root = Path(__file__).resolve().parents[3]
        resolved_path = repo_root / prompt_path
        return resolved_path.read_text(encoding="utf-8")
