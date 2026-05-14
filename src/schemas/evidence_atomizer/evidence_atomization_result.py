"""Final output schema for the Evidence Atomizer.

EvidenceAtomizationResult is the only formal output package of the Evidence
Atomizer. It packages evidence atoms, transformation links, deferred items,
and atomization warnings for later reasoning phases.

It must not include diagnosis, HypothesisState, support/refute relationships,
ActionPlan, UpdateTrace, Conflict, SafetyGateResult, or ArbitrationResult.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.utils.id_generator import generate_atomization_result_id

from .atomization_warning import AtomizationWarning
from .common import (
    CaseID,
    EvidenceAtomizationResultID,
    InputID,
    StageID,
    ValidationSeverity,
    normalize_optional_text,
    validate_no_forbidden_schema_fields,
)
from .deferred_item import DeferredStructuredItem
from .evidence_atom import EvidenceAtom
from .item_evidence_link import ItemEvidenceLink


class EvidenceAtomizationResult(BaseModel):
    """Validated output package of the Evidence Atomizer.

    EvidenceAtomizationResult answers one question:

        What source-grounded evidence atoms and atomization metadata were
        produced from one validated CaseStructuringResult?

    It does not answer what diagnosis is likely, what an atom supports or
    refutes, what treatment should be recommended, what conflicts exist, what
    update should be made, whether a safety gate fired, or how agents should be
    arbitrated.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    atomization_result_id: EvidenceAtomizationResultID = Field(
        default_factory=generate_atomization_result_id,
        description="Unique id for this evidence atomization result.",
    )

    case_id: CaseID = Field(
        ...,
        description="Case id this atomization result belongs to.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id this atomization result was derived from.",
    )

    stage_id: StageID | None = Field(
        default=None,
        description="Optional StageContext id for this atomization result.",
    )

    source_structuring_result_id: str | None = Field(
        default=None,
        description="Optional source CaseStructuringResult id if one exists.",
    )

    evidence_atoms: list[EvidenceAtom] = Field(
        default_factory=list,
        description="Evidence atoms produced by the Evidence Atomizer.",
    )

    item_to_evidence_links: list[ItemEvidenceLink] = Field(
        default_factory=list,
        description="Links explaining how structured items became evidence atoms.",
    )

    deferred_items: list[DeferredStructuredItem] = Field(
        default_factory=list,
        description="Structured items deferred instead of forced into evidence atoms.",
    )

    atomization_warnings: list[AtomizationWarning] = Field(
        default_factory=list,
        description="Warnings or errors produced during evidence atomization.",
    )

    ready_for_hypothesis_state: bool = Field(
        ...,
        description=(
            "Whether the atomization output is ready for later hypothesis-state "
            "generation. This is not a hypothesis judgment."
        ),
    )

    @field_validator("source_structuring_result_id", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize blank optional source result id to None."""
        return normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_atom_identity_consistency(self) -> "EvidenceAtomizationResult":
        """Validate that all evidence atoms match result identity fields."""
        mismatched_case_atoms = [
            atom.evidence_id
            for atom in self.evidence_atoms
            if atom.case_id != self.case_id
        ]

        mismatched_input_atoms = [
            atom.evidence_id
            for atom in self.evidence_atoms
            if atom.input_id != self.input_id
        ]

        errors: list[str] = []

        if mismatched_case_atoms:
            errors.append(f"case_id mismatches={mismatched_case_atoms}")

        if mismatched_input_atoms:
            errors.append(f"input_id mismatches={mismatched_input_atoms}")

        if self.stage_id is not None:
            mismatched_stage_atoms = [
                atom.evidence_id
                for atom in self.evidence_atoms
                if atom.stage_id != self.stage_id
            ]
            if mismatched_stage_atoms:
                errors.append(f"stage_id mismatches={mismatched_stage_atoms}")

        if errors:
            raise ValueError(
                "All EvidenceAtom identity fields must match the "
                "EvidenceAtomizationResult. " + "; ".join(errors)
            )

        return self

    @model_validator(mode="after")
    def validate_unique_evidence_ids(self) -> "EvidenceAtomizationResult":
        """Validate that evidence atom ids are unique."""
        self._raise_if_duplicate(
            values=[atom.evidence_id for atom in self.evidence_atoms],
            label="evidence_atoms.evidence_id",
        )
        return self

    @model_validator(mode="after")
    def validate_link_references(self) -> "EvidenceAtomizationResult":
        """Validate that item-to-evidence links reference existing atoms."""
        evidence_ids = {atom.evidence_id for atom in self.evidence_atoms}
        missing_refs: list[dict[str, str]] = []

        for link in self.item_to_evidence_links:
            for evidence_id in link.evidence_ids:
                if evidence_id not in evidence_ids:
                    missing_refs.append(
                        {
                            "item_id": link.item_id,
                            "missing_evidence_id": evidence_id,
                        }
                    )

        if missing_refs:
            raise ValueError(
                "Every ItemEvidenceLink.evidence_ids entry must reference an "
                f"existing EvidenceAtom.evidence_id. Missing refs: {missing_refs}"
            )

        return self

    @model_validator(mode="after")
    def validate_readiness_consistency(self) -> "EvidenceAtomizationResult":
        """Validate readiness flags against atoms, deferrals, and warnings."""
        if self.evidence_atoms:
            if self.ready_for_hypothesis_state:
                return self
        elif self.ready_for_hypothesis_state:
            raise ValueError(
                "ready_for_hypothesis_state must be False when evidence_atoms is empty."
            )

        has_warning_or_error = any(
            warning.severity in {
                ValidationSeverity.WARNING,
                ValidationSeverity.ERROR,
            }
            for warning in self.atomization_warnings
        )

        if not self.deferred_items and not has_warning_or_error:
            raise ValueError(
                "ready_for_hypothesis_state=False requires at least one deferred "
                "item or atomization warning with severity warning or error."
            )

        return self

    @model_validator(mode="after")
    def validate_schema_boundary(self) -> "EvidenceAtomizationResult":
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
