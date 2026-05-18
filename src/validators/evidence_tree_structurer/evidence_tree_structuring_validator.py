"""Validation report schemas for Evidence Tree Structurer execution."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.evidence_tree_structurer.common import (
    EvidenceTreeNodeID,
    ItemID,
    SpanID,
    ValidationSeverity,
    normalize_optional_text,
    require_non_empty_text,
)


class EvidenceTreeStructuringValidationIssue(BaseModel):
    """One Evidence Tree Structurer validation issue or warning."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity = Field(
        ...,
        description="Severity of this validation issue.",
    )
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    related_item_id: ItemID | None = None
    related_tree_node_id: EvidenceTreeNodeID | None = None
    related_span_id: SpanID | None = None

    @field_validator("code", "message", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "Required text fields")

    @field_validator(
        "related_item_id",
        "related_tree_node_id",
        "related_span_id",
        mode="after",
    )
    @classmethod
    def optional_ids_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)


class EvidenceTreeStructuringValidationReport(BaseModel):
    """Validation report for Evidence Tree Structurer execution."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    accepted: bool = Field(
        ...,
        description="True only when validation produced no ERROR issues.",
    )
    issues: list[EvidenceTreeStructuringValidationIssue] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(
            issue.severity == ValidationSeverity.WARNING for issue in self.issues
        )

    @model_validator(mode="after")
    def validate_acceptance_matches_errors(
        self,
    ) -> "EvidenceTreeStructuringValidationReport":
        expected_accepted = not self.has_errors
        if self.accepted != expected_accepted:
            raise ValueError(
                "accepted must be True only when there are no ERROR issues."
            )
        return self
