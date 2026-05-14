"""Item-to-evidence link schema for the Evidence Atomizer.

ItemEvidenceLink records how one StructuredClinicalItem was transformed into
one or more EvidenceAtom objects. It tracks atomization provenance without
assigning diagnosis support/refute relationships or downstream actions.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import (
    AtomizationTransformationType,
    EvidenceID,
    ItemID,
    normalize_optional_text,
    reject_reasoning_scope_text,
    validate_no_forbidden_schema_fields,
)


class ItemEvidenceLink(BaseModel):
    """Transformation link from one structured item to evidence atoms.

    This schema explains the atomization operation only. It must not encode
    diagnoses, hypotheses, evidence polarity, treatment recommendations,
    conflicts, update traces, safety gates, or arbitration results.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: ItemID = Field(
        ...,
        description="StructuredClinicalItem id being transformed.",
    )

    evidence_ids: list[EvidenceID] = Field(
        default_factory=list,
        description="EvidenceAtom ids produced from this structured item.",
    )

    transformation_type: AtomizationTransformationType = Field(
        ...,
        description="How this structured item was atomized.",
    )

    explanation: str | None = Field(
        default=None,
        description="Optional explanation of non-trivial atomization.",
    )

    @field_validator("explanation", mode="after")
    @classmethod
    def optional_explanation_must_not_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize optional blank explanation to None."""
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_transformation_consistency(self) -> "ItemEvidenceLink":
        """Validate evidence refs and required explanations."""
        requires_no_evidence = {
            AtomizationTransformationType.DEFERRED,
            AtomizationTransformationType.DROPPED,
        }

        if (
            self.transformation_type not in requires_no_evidence
            and not self.evidence_ids
        ):
            raise ValueError(
                "evidence_ids must contain at least one EvidenceID unless "
                "transformation_type is deferred or dropped."
            )

        requires_explanation = {
            AtomizationTransformationType.SPLIT,
            AtomizationTransformationType.MERGED,
            AtomizationTransformationType.DEFERRED,
            AtomizationTransformationType.DROPPED,
        }

        if self.transformation_type in requires_explanation:
            cleaned = reject_reasoning_scope_text(
                self.explanation,
                "explanation",
            )
            if cleaned is None:
                raise ValueError(
                    "explanation is required when transformation_type is "
                    "split, merged, deferred, or dropped."
                )

        elif self.explanation is not None:
            reject_reasoning_scope_text(self.explanation, "explanation")

        return self

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "ItemEvidenceLink":
        """Validate that ItemEvidenceLink does not expose downstream fields."""
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self
