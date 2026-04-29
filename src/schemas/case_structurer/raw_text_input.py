"""Raw free-text input schema for the Case Structurer.

RawTextInput is the system wrapper around user-provided free text.
It does not classify the clinical content and does not infer whether
the text is a full pasted record, follow-up note, lab report, MDT note,
or manual supplement.

Content classification belongs to StageContext, ClinicalSection, and
StructuredClinicalItem.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.utils.id_generator import generate_input_id

from .common import CaseID, InputID


def _utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)



class RawTextInput(BaseModel):
    """System wrapper for one piece of user-provided free text.

    This schema records only facts known at ingestion time:
    the raw text, its case-level identity, its input identity,
    and basic ingestion metadata.

    It must not infer the clinical type of the content.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    input_id: InputID = Field(
        default_factory=generate_input_id,
        description="Unique id for this raw text input.",
    )

    case_id: CaseID = Field(
        ...,
        description="Case id this input belongs to. Generated or selected by the system.",
    )


    raw_text: str = Field(
        ...,
        min_length=1,
        description="Original user-provided free text. Must be preserved unchanged except trimming outer whitespace.",
    )

    received_at: datetime = Field(
        default_factory=_utc_now,
        description="Timezone-aware timestamp when the system received this input.",
    )

    input_order: int | None = Field(
        default=None,
        ge=1,
        description="Optional order of this input within the same case. This is ingestion order, not clinical stage.",
    )

    parent_input_id: InputID | None = Field(
        default=None,
        description="Optional id of a previous input this text explicitly supplements.",
    )

    @field_validator("raw_text")
    @classmethod
    def raw_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only input."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("raw_text must not be empty.")
        return cleaned