"""Clinical attribute schema for Attribute Extractor output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.case_structurer.source_span import SourceSpan
from src.utils.id_generator import generate_attribute_id

from .attribute_role import AttributeRole
from .common import AttributeID, CaseID, ConfidenceLevel, InputID, ItemID


class ClinicalAttribute(BaseModel):
    """A source-copied attribute span role-labeled from a StructuredClinicalItem."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    attribute_id: AttributeID = Field(
        default_factory=generate_attribute_id,
        description="Unique id for this clinical attribute.",
    )
    case_id: CaseID = Field(..., description="Case id this attribute belongs to.")
    input_id: InputID = Field(
        ...,
        description="RawTextInput id this attribute was extracted from.",
    )
    source_item_id: ItemID = Field(
        ...,
        description="StructuredClinicalItem.item_id that owns this attribute.",
    )
    attribute_role: AttributeRole = Field(
        ...,
        description="Role label assigned to this copied source span.",
    )
    span_text: str = Field(
        ...,
        min_length=1,
        description="Exact continuous source substring selected from item source text.",
    )
    source_span: SourceSpan = Field(
        ...,
        description="Raw-text provenance for span_text.",
    )
    normalized_value: str | int | float | None = Field(
        default=None,
        description="Optional lightweight normalized scalar value.",
    )
    normalized_unit: str | None = Field(
        default=None,
        description="Optional lightweight normalized unit.",
    )
    normalized_text: str | None = Field(
        default=None,
        description="Optional lightweight normalized text.",
    )
    extraction_confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence in span-role extraction, not diagnostic confidence.",
    )
    notes: str | None = Field(
        default=None,
        description="Optional extraction note. Must not contain downstream reasoning.",
    )

    @field_validator("span_text", mode="after")
    @classmethod
    def span_text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("span_text must not be empty.")
        return cleaned

    @field_validator(
        "normalized_unit",
        "normalized_text",
        "notes",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("normalized_value", mode="after")
    @classmethod
    def normalized_value_empty_string_to_none(
        cls,
        value: str | int | float | None,
    ) -> str | int | float | None:
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value

    @model_validator(mode="after")
    def validate_source_span_matches_input(self) -> "ClinicalAttribute":
        if self.source_span.input_id != self.input_id:
            raise ValueError(
                "ClinicalAttribute.source_span.input_id must match input_id."
            )
        if self.source_span.quoted_text != self.span_text:
            raise ValueError(
                "ClinicalAttribute.source_span.quoted_text must equal span_text."
            )
        return self
