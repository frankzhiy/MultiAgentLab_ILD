"""Final output schema for the Attribute Extractor."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.utils.id_generator import generate_attribute_extraction_result_id

from .clinical_attribute import ClinicalAttribute
from .common import (
    AttributeExtractionResultID,
    AttributeID,
    CaseID,
    CaseStructuringResultID,
    InputID,
    ItemID,
    ValidationSeverity,
)


class AttributeExtractionWarning(BaseModel):
    """Warning or error produced during attribute extraction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    related_item_id: ItemID | None = None
    related_attribute_id: AttributeID | None = None

    @field_validator("code", "message", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required text fields must not be empty.")
        return cleaned

    @field_validator(
        "related_item_id",
        "related_attribute_id",
        mode="after",
    )
    @classmethod
    def optional_ids_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AttributeExtractionResult(BaseModel):
    """Validated Attribute Extractor result for one CaseStructuringResult."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    attribute_extraction_result_id: AttributeExtractionResultID = Field(
        default_factory=generate_attribute_extraction_result_id,
        description="Unique id for this AttributeExtractionResult.",
    )
    case_id: CaseID
    input_id: InputID
    source_structuring_result_id: CaseStructuringResultID
    clinical_attributes: list[ClinicalAttribute] = Field(default_factory=list)
    extraction_warnings: list[AttributeExtractionWarning] = Field(default_factory=list)
    ready_for_evidence_atomization: bool = True

    @field_validator("source_structuring_result_id", mode="after")
    @classmethod
    def source_result_id_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("source_structuring_result_id must not be empty.")
        return cleaned

    @model_validator(mode="after")
    def validate_attribute_identity_consistency(self) -> "AttributeExtractionResult":
        mismatched_attributes = [
            attribute.attribute_id
            for attribute in self.clinical_attributes
            if attribute.case_id != self.case_id or attribute.input_id != self.input_id
        ]
        if mismatched_attributes:
            raise ValueError(
                "All ClinicalAttribute case_id/input_id values must match the "
                f"AttributeExtractionResult. Mismatches: {mismatched_attributes}"
            )
        return self

    @model_validator(mode="after")
    def validate_unique_attribute_ids(self) -> "AttributeExtractionResult":
        seen: set[str] = set()
        duplicates: list[str] = []
        for attribute in self.clinical_attributes:
            if attribute.attribute_id in seen and attribute.attribute_id not in duplicates:
                duplicates.append(attribute.attribute_id)
            seen.add(attribute.attribute_id)
        if duplicates:
            raise ValueError(f"Duplicate attribute_id values found: {duplicates}")
        return self

    @model_validator(mode="after")
    def validate_readiness_has_warning_when_false(self) -> "AttributeExtractionResult":
        if self.ready_for_evidence_atomization:
            return self
        has_warning_or_error = any(
            warning.severity in {
                ValidationSeverity.WARNING,
                ValidationSeverity.ERROR,
            }
            for warning in self.extraction_warnings
        )
        if not has_warning_or_error:
            raise ValueError(
                "ready_for_evidence_atomization=False requires at least one "
                "extraction warning with severity warning or error."
            )
        return self
