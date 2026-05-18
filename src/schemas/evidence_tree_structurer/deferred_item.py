"""Deferred structured item schema for the Evidence Tree Structurer.

DeferredStructuredItem represents a StructuredClinicalItem that cannot safely
become an EvidenceTree. Deferring an item is safer than forcing ambiguous or
non-clinical text into the evidence ledger.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import (
    DeferredReason,
    ItemID,
    SpanID,
    reject_reasoning_scope_text,
    require_non_empty_text,
    validate_no_forbidden_schema_fields,
)


class DeferredStructuredItem(BaseModel):
    """Structured item that the Evidence Tree Structurer intentionally deferred.

    This object records tree-structuring safety and provenance only. It must not
    encode diagnoses, hypotheses, treatment recommendations, conflicts,
    update traces, safety gates, or arbitration outcomes.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: ItemID = Field(
        ...,
        description="StructuredClinicalItem id that could not be structured safely.",
    )

    reason: DeferredReason = Field(
        ...,
        description="Reason this structured item was deferred.",
    )

    explanation: str = Field(
        ...,
        min_length=1,
        description="Tree-structuring-scope explanation for deferring this item.",
    )

    related_span_ids: list[SpanID] = Field(
        default_factory=list,
        description="SourceSpan ids related to this deferred item.",
    )

    @field_validator("explanation", mode="after")
    @classmethod
    def explanation_must_not_be_blank(cls, value: str) -> str:
        """Reject empty explanations and downstream reasoning content."""
        cleaned = require_non_empty_text(value, "explanation")
        scoped = reject_reasoning_scope_text(cleaned, "explanation")
        if scoped is None:
            raise ValueError("explanation must not be empty.")
        return scoped

    @model_validator(mode="after")
    def validate_span_requirement(self) -> "DeferredStructuredItem":
        """Require spans unless the deferral is about missing source spans."""
        if (
            self.reason != DeferredReason.INSUFFICIENT_SOURCE_SPAN
            and not self.related_span_ids
        ):
            raise ValueError(
                "related_span_ids can be empty only when reason is "
                "insufficient_source_span."
            )

        return self

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "DeferredStructuredItem":
        """Validate that DeferredStructuredItem does not expose downstream fields."""
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
