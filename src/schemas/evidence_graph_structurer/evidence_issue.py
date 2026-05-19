"""EvidenceStructuringIssue schema for the Evidence Graph Structurer.

Replaces the legacy TreeStructuringWarning. Carries quality issues produced
by the assertion resolver, frame assembler, relation extractor, graph
composer, and graph validator.
"""

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


class EvidenceStructuringIssue(BaseModel):
    """One quality issue produced during evidence graphlet structuring.

    Reports source-grounding, schema, frame, node, or relation quality only.
    Must not encode diagnosis, hypothesis, treatment, conflict, update,
    safety gate, or arbitration decisions.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity = Field(
        ...,
        description="Severity of this evidence-structuring issue.",
    )

    code: str = Field(
        ...,
        min_length=1,
        description="Stable machine-readable evidence-structuring issue code.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable evidence-structuring quality message.",
    )

    related_item_id: ItemID | None = Field(
        default=None,
        description="Optional related StructuredClinicalItem id.",
    )

    related_assertion_id: str | None = Field(
        default=None,
        description="Optional related ClinicalObjectAssertion id.",
    )

    related_frame_id: str | None = Field(
        default=None,
        description="Optional related EvidenceFrame id.",
    )

    related_node_id: str | None = Field(
        default=None,
        description="Optional related EvidenceNode id.",
    )

    related_relation_id: str | None = Field(
        default=None,
        description="Optional related EvidenceRelation id.",
    )

    related_span_id: SpanID | None = Field(
        default=None,
        description="Optional related SourceSpan id.",
    )

    details: str | None = Field(
        default=None,
        description="Optional extra detail or context for this issue.",
    )

    @field_validator("code", mode="after")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "code")

    @field_validator("message", mode="after")
    @classmethod
    def message_must_stay_in_scope(cls, value: str) -> str:
        cleaned = require_non_empty_text(value, "message")
        scoped = reject_reasoning_scope_text(cleaned, "message")
        if scoped is None:
            raise ValueError("message must not be empty.")
        return scoped

    @field_validator(
        "related_item_id",
        "related_assertion_id",
        "related_frame_id",
        "related_node_id",
        "related_relation_id",
        "related_span_id",
        "details",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "EvidenceStructuringIssue":
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
