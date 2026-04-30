from __future__ import annotations

from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.utils.id_generator import generate_case_id


class RawInputBuilder:
    """Build the system-controlled RawTextInput wrapper."""

    def build(
        self,
        raw_text: str,
        case_id: str | None = None,
        input_order: int = 1,
        parent_input_id: str | None = None,
    ) -> RawTextInput:
        return RawTextInput(
            case_id=case_id or generate_case_id(),
            raw_text=raw_text,
            input_order=input_order,
            parent_input_id=parent_input_id,
        )
