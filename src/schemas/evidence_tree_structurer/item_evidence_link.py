"""Item-to-tree link schema for the Evidence Tree Structurer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import (
    TreeStructuringTransformationType,
    EvidenceTreeID,
    ItemID,
    normalize_optional_text,
    reject_reasoning_scope_text,
    validate_no_forbidden_schema_fields,
)


class ItemEvidenceTreeLink(BaseModel):
    """Transformation link from one structured item to an EvidenceTree.

    This schema records the primary tree-shaped evidence output for an item.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: ItemID = Field(
        ...,
        description="StructuredClinicalItem id represented by this evidence tree.",
    )

    tree_ids: list[EvidenceTreeID] = Field(
        default_factory=list,
        description="EvidenceTree ids produced from this structured item.",
    )

    transformation_type: TreeStructuringTransformationType = Field(
        ...,
        description="How this structured item became tree-shaped evidence.",
    )

    explanation: str | None = Field(
        default=None,
            description="Optional explanation of non-trivial tree structuring.",
    )

    @field_validator("explanation", mode="after")
    @classmethod
    def optional_explanation_must_not_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_transformation_consistency(self) -> "ItemEvidenceTreeLink":
        if (
            self.transformation_type
            not in {
                TreeStructuringTransformationType.DEFERRED,
                TreeStructuringTransformationType.DROPPED,
            }
            and not self.tree_ids
        ):
            raise ValueError(
                "tree_ids must contain at least one EvidenceTreeID unless "
                "transformation_type is deferred or dropped."
            )

        if self.explanation is not None:
            reject_reasoning_scope_text(self.explanation, "explanation")

        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
