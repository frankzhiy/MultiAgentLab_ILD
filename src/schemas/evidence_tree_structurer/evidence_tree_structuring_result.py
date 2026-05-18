"""Final tree output schema for the Evidence Tree Structurer.

EvidenceTreeStructuringResult is the formal output package of the Evidence
Tree Structurer. It packages evidence trees, item-to-tree links, deferred
items, and tree-structuring warnings for later reasoning phases.

It must not include diagnosis, HypothesisState, support/refute relationships,
ActionPlan, UpdateTrace, Conflict, SafetyGateResult, or ArbitrationResult.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.case_structurer.common import CaseStructuringResultID
from src.utils.id_generator import generate_tree_structuring_result_id

from .tree_structuring_warning import TreeStructuringWarning
from .common import (
    CaseID,
    EvidenceTreeStructuringResultID,
    InputID,
    StageID,
    ValidationSeverity,
    normalize_optional_text,
    validate_no_forbidden_schema_fields,
)
from .deferred_item import DeferredStructuredItem
from .evidence_tree import EvidenceTree
from .item_evidence_link import ItemEvidenceTreeLink


class EvidenceTreeStructuringResult(BaseModel):
    """Validated output package of the Evidence Tree Structurer.

    EvidenceTreeStructuringResult answers one question:

        What source-grounded evidence trees and tree-structuring metadata were
        produced from one validated CaseStructuringResult?

    It does not answer what diagnosis is likely, what a node supports or
    refutes, what treatment should be recommended, what conflicts exist, what
    update should be made, whether a safety gate fired, or how agents should be
    arbitrated.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    tree_structuring_result_id: EvidenceTreeStructuringResultID = Field(
        default_factory=generate_tree_structuring_result_id,
        description="Unique id for this evidence tree structuring result.",
    )

    case_id: CaseID = Field(
        ...,
        description="Case id this tree structuring result belongs to.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id this tree structuring result was derived from.",
    )

    stage_id: StageID | None = Field(
        default=None,
        description="Optional StageContext id for this tree structuring result.",
    )

    source_structuring_result_id: CaseStructuringResultID | None = Field(
        default=None,
        description=(
            "Optional CaseStructuringResult.case_structuring_result_id that "
            "this tree structuring result was derived from."
        ),
    )

    evidence_trees: list[EvidenceTree] = Field(
        default_factory=list,
        description="Tree-shaped structured evidence produced by the Evidence Tree Structurer.",
    )

    item_to_tree_links: list[ItemEvidenceTreeLink] = Field(
        default_factory=list,
        description="Links explaining how structured items became evidence trees.",
    )

    deferred_items: list[DeferredStructuredItem] = Field(
        default_factory=list,
        description="Structured items deferred instead of forced into evidence trees.",
    )

    tree_structuring_warnings: list[TreeStructuringWarning] = Field(
        default_factory=list,
        description="Warnings or errors produced during evidence tree structuring.",
    )

    ready_for_hypothesis_state: bool = Field(
        ...,
        description=(
            "Whether the tree output is ready for later hypothesis-state "
            "generation. This is not a hypothesis judgment."
        ),
    )

    @field_validator("source_structuring_result_id", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize blank optional source result id to None."""
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_unique_tree_ids(self) -> "EvidenceTreeStructuringResult":
        """Validate that evidence tree ids are unique."""
        self._raise_if_duplicate(
            values=[tree.tree_id for tree in self.evidence_trees],
            label="evidence_trees.tree_id",
        )
        return self

    @model_validator(mode="after")
    def validate_link_references(self) -> "EvidenceTreeStructuringResult":
        """Validate that item/tree links reference existing trees."""
        tree_ids = {tree.tree_id for tree in self.evidence_trees}
        missing_tree_refs: list[dict[str, str]] = []
        for link in self.item_to_tree_links:
            for tree_id in link.tree_ids:
                if tree_id not in tree_ids:
                    missing_tree_refs.append(
                        {
                            "item_id": link.item_id,
                            "missing_tree_id": tree_id,
                        }
                    )

        if missing_tree_refs:
            raise ValueError(
                "Every ItemEvidenceTreeLink.tree_ids entry must point to an "
                f"existing EvidenceTree. Missing refs: {missing_tree_refs}"
            )
        return self

    @model_validator(mode="after")
    def validate_readiness_consistency(self) -> "EvidenceTreeStructuringResult":
        """Validate readiness flags against trees, deferrals, and warnings."""
        if self.evidence_trees:
            if self.ready_for_hypothesis_state:
                return self
        elif self.ready_for_hypothesis_state:
            raise ValueError(
                "ready_for_hypothesis_state must be False when evidence_trees is empty."
            )

        has_warning_or_error = any(
            warning.severity in {
                ValidationSeverity.WARNING,
                ValidationSeverity.ERROR,
            }
            for warning in self.tree_structuring_warnings
        )

        if not self.deferred_items and not has_warning_or_error:
            raise ValueError(
                "ready_for_hypothesis_state=False requires at least one deferred "
                "item or tree-structuring warning with severity warning or error."
            )

        return self

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "EvidenceTreeStructuringResult":
        """Validate that the result schema does not expose downstream fields."""
        validate_no_forbidden_schema_fields(
            model_name=type(self).__name__,
            field_names=set(type(self).model_fields),
        )
        return self

    @staticmethod
    def _raise_if_duplicate(values: list[object], label: str) -> None:
        """Raise a ValueError if duplicate values are found."""
        seen: set[object] = set()
        duplicates: list[object] = []

        for value in values:
            if value in seen and value not in duplicates:
                duplicates.append(value)
            seen.add(value)

        if duplicates:
            raise ValueError(f"Duplicate values found in {label}: {duplicates}")
