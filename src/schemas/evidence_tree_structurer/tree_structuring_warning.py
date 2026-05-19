"""TreeStructuring warning schema for the Evidence Tree Structurer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import (
    ItemID,
    SpanID,
    ValidationSeverity,
    normalize_optional_text,
    reject_reasoning_scope_text,
    require_non_empty_text,
    validate_no_forbidden_schema_fields,
)


class TreeStructuringWarning(BaseModel):
    """Warning or error produced during evidence tree structuring.

    TreeStructuringWarning is analogous to StructuringWarning, but it belongs to
    Evidence Tree Structurer, not Case Structurer. It reports tree-structuring or
    validation quality only and must not encode diagnosis, hypothesis,
    treatment, conflict, update, safety gate, or arbitration decisions.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity = Field(
        ...,
        description="Severity of this tree-structuring warning.",
    )

    code: str = Field(
        ...,
        min_length=1,
        description="Stable machine-readable tree-structuring warning code.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable tree-structuring or validation quality message.",
    )

    related_item_id: ItemID | None = Field(
        default=None,
        description="Optional related StructuredClinicalItem id.",
    )

    related_span_id: SpanID | None = Field(
        default=None,
        description="Optional related SourceSpan id.",
    )

    @field_validator("code", mode="after")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        """Reject empty warning codes."""
        return require_non_empty_text(value, "code")

    @field_validator("message", mode="after")
    @classmethod
    def message_must_stay_in_tree_structuring_scope(cls, value: str) -> str:
        """Reject empty messages and downstream reasoning content."""
        cleaned = require_non_empty_text(value, "message")
        scoped = reject_reasoning_scope_text(cleaned, "message")
        if scoped is None:
            raise ValueError("message must not be empty.")
        return scoped

    @field_validator(
        "related_item_id",
        "related_span_id",
        mode="after",
    )
    @classmethod
    def optional_ids_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize blank optional id fields to None."""
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "TreeStructuringWarning":
        """Validate that TreeStructuringWarning does not expose downstream fields."""
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
