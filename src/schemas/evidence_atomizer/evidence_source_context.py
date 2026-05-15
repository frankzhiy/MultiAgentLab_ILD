"""Clinical-section provenance context for EvidenceAtom."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.clinical_section import ClinicalSectionType
from src.schemas.case_structurer.common import SectionID


class EvidenceSourceContext(BaseModel):
    """Document-section provenance context for one EvidenceAtom.

    EvidenceSourceContext records where an evidence atom came from in the
    source document structure. It is provenance metadata, not diagnostic
    reasoning and not an evidence polarity judgment.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    section_id: SectionID = Field(
        ...,
        description="ClinicalSection id that contributed to this evidence atom.",
    )

    section_type: ClinicalSectionType = Field(
        ...,
        description=(
            "Broad clinical-document section type, such as "
            "history_of_present_illness, past_medical_history, imaging, "
            "laboratory_test, treatment_history, or family_history."
        ),
    )

    section_title: str | None = Field(
        default=None,
        description=(
            "Optional original or normalized section heading, such as 主诉, "
            "现病史, 既往史, 辅助检查. None if no heading is available."
        ),
    )

    @field_validator("section_title")
    @classmethod
    def optional_title_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None
