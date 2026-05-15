from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.attribute_extractor.common import (
    AttributeID,
    ItemID,
    ValidationSeverity,
)
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)


class AttributeExtractionValidationIssue(BaseModel):
    """One deterministic Attribute Extractor validation issue."""

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


class AttributeExtractionValidationReport(BaseModel):
    """Validation report for Attribute Extractor output."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    accepted: bool
    issues: list[AttributeExtractionValidationIssue] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    @model_validator(mode="after")
    def validate_acceptance_matches_errors(
        self,
    ) -> "AttributeExtractionValidationReport":
        expected_accepted = not self.has_errors
        if self.accepted != expected_accepted:
            raise ValueError(
                "accepted must be True only when there are no ERROR issues."
            )
        return self


class AttributeExtractionValidationResult(BaseModel):
    """Attribute Extractor output plus deterministic validation report."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    attribute_extraction_result: AttributeExtractionResult
    validation_report: AttributeExtractionValidationReport

    @property
    def accepted(self) -> bool:
        return self.validation_report.accepted
