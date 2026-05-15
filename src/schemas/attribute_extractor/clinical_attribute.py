"""Clinical attribute schema for Attribute Extractor output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.case_structurer.source_span import SourceSpan
from src.utils.id_generator import generate_attribute_id

from .attribute_role import AttributeRole
from .attribute_scope import AttributeScope
from .common import AttributeID, CaseID, ConfidenceLevel, InputID, ItemID


class ClinicalAttribute(BaseModel):
    """A target-grounded attribute modifier relation on a StructuredClinicalItem.

    ClinicalAttribute is not a standalone clinical fact. It answers:
    what modifier span appears in this item, what role it plays, and what
    source-copied object or phrase it modifies.
    """

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
    span_text: str = Field(
        ...,
        min_length=1,
        description="Exact continuous attribute modifier substring from item source text.",
    )
    attribute_role: AttributeRole = Field(
        ...,
        description="Semantic role played by span_text as a modifier.",
    )
    attribute_scope: AttributeScope = Field(
        ...,
        description=(
            "Scope of the source-copied phrase modified by this attribute: the "
            "whole item, a local phrase, multiple coordinated objects, or uncertain."
        ),
    )
    applies_to_text: str | None = Field(
        default=None,
        description=(
            "The source-copied object or phrase that this attribute modifies. "
            "When present, it must be a continuous substring of the source item's text."
        ),
    )
    context_text: str = Field(
        ...,
        min_length=1,
        description=(
            "The full source item text that provides context for interpreting this "
            "attribute. This should be filled deterministically from the owning "
            "StructuredClinicalItem."
        ),
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
        description="Confidence in extracting this attribute relation, not diagnostic confidence.",
    )
    notes: str | None = Field(
        default=None,
        description="Optional extraction note. Must not contain downstream reasoning.",
    )

    @field_validator("span_text", "context_text", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required ClinicalAttribute text must not be empty.")
        return cleaned

    @field_validator(
        "applies_to_text",
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
