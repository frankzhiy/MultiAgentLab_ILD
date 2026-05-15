"""Deterministic validation for Evidence Atomizer output.

Schema validity is not enough for Evidence Atomizer results. A result can
pass Pydantic validation while still failing to prove that its evidence atoms,
links, and deferrals are grounded in the upstream CaseStructuringResult.

This validator is the deterministic gate before Evidence Atomizer output can
be used downstream. It checks provenance and cross-object grounding only. It
does not judge diagnosis correctness, assign support/refute relationships,
create hypotheses, recommend treatment, detect conflicts, run safety gates, or
arbitrate between agents.
"""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.attribute_extractor.common import AttributeID
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.evidence_atomizer.common import (
    AtomizationTransformationType,
    EvidenceID,
    ItemID,
    SpanID,
    ValidationSeverity,
    normalize_optional_text,
    require_non_empty_text,
)
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)


class EvidenceAtomizationValidationIssue(BaseModel):
    """One deterministic Evidence Atomizer validation issue."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity = Field(
        ...,
        description="Severity of this validation issue.",
    )

    code: str = Field(
        ...,
        min_length=1,
        description="Stable machine-readable issue code.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable validation issue message.",
    )

    related_item_id: ItemID | None = Field(
        default=None,
        description="Optional related StructuredClinicalItem id.",
    )

    related_evidence_id: EvidenceID | None = Field(
        default=None,
        description="Optional related EvidenceAtom id.",
    )

    related_span_id: SpanID | None = Field(
        default=None,
        description="Optional related SourceSpan id.",
    )

    related_attribute_id: AttributeID | None = Field(
        default=None,
        description="Optional related ClinicalAttribute id.",
    )

    @field_validator("code", "message", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only required text fields."""
        return require_non_empty_text(value, "Required text fields")

    @field_validator(
        "related_item_id",
        "related_evidence_id",
        "related_span_id",
        "related_attribute_id",
        mode="after",
    )
    @classmethod
    def optional_ids_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize blank optional id fields to None."""
        return normalize_optional_text(value)


class EvidenceAtomizationValidationReport(BaseModel):
    """Validation report for cross-object Evidence Atomizer grounding."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    accepted: bool = Field(
        ...,
        description="True only when validation produced no ERROR issues.",
    )

    issues: list[EvidenceAtomizationValidationIssue] = Field(
        default_factory=list,
        description="Deterministic cross-object validation issues.",
    )

    @property
    def has_errors(self) -> bool:
        """Return whether the report contains any ERROR issue."""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Return whether the report contains any WARNING issue."""
        return any(
            issue.severity == ValidationSeverity.WARNING for issue in self.issues
        )

    @model_validator(mode="after")
    def validate_acceptance_matches_errors(
        self,
    ) -> "EvidenceAtomizationValidationReport":
        """Ensure accepted is derived from ERROR-level issues."""
        expected_accepted = not self.has_errors
        if self.accepted != expected_accepted:
            raise ValueError(
                "accepted must be True only when there are no ERROR issues."
            )

        return self


class EvidenceAtomizationValidator:
    """Validate EvidenceAtomizationResult against CaseStructuringResult.

    This validator checks deterministic provenance and cross-object grounding.
    It assumes both objects are already schema-valid and verifies that the
    atomization output is actually traceable to the structured case input.
    """

    def validate(
        self,
        *,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        atomization_result: EvidenceAtomizationResult,
    ) -> EvidenceAtomizationValidationReport:
        """Validate atomization output without mutating either input."""
        issues: list[EvidenceAtomizationValidationIssue] = []
        items_by_id = _structured_items_by_id(structuring_result)

        issues.extend(
            self._validate_result_identity(
                structuring_result=structuring_result,
                attribute_result=attribute_result,
                atomization_result=atomization_result,
            )
        )
        issues.extend(
            self._validate_evidence_atom_sources(
                structuring_result=structuring_result,
                attribute_result=attribute_result,
                atomization_result=atomization_result,
                items_by_id=items_by_id,
            )
        )
        issues.extend(
            self._validate_item_evidence_links(
                atomization_result=atomization_result,
                items_by_id=items_by_id,
            )
        )
        issues.extend(
            self._validate_deferred_items(
                atomization_result=atomization_result,
                items_by_id=items_by_id,
            )
        )
        issues.extend(
            self._validate_item_coverage(
                structuring_result=structuring_result,
                atomization_result=atomization_result,
            )
        )
        issues.extend(self._validate_deferred_link_consistency(atomization_result))
        issues.extend(self._validate_possible_duplicate_atoms(atomization_result))

        return EvidenceAtomizationValidationReport(
            accepted=not any(
                issue.severity == ValidationSeverity.ERROR for issue in issues
            ),
            issues=issues,
        )

    def _validate_result_identity(
        self,
        *,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        atomization_result: EvidenceAtomizationResult,
    ) -> list[EvidenceAtomizationValidationIssue]:
        issues: list[EvidenceAtomizationValidationIssue] = []

        if atomization_result.case_id != structuring_result.input.case_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="case_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.case_id must match "
                        "CaseStructuringResult.input.case_id."
                    ),
                )
            )

        if atomization_result.input_id != structuring_result.input.input_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="input_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.input_id must match "
                        "CaseStructuringResult.input.input_id."
                    ),
                )
            )

        if atomization_result.case_id != attribute_result.case_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="attribute_case_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.case_id must match "
                        "AttributeExtractionResult.case_id."
                    ),
                )
            )

        if atomization_result.input_id != attribute_result.input_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="attribute_input_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.input_id must match "
                        "AttributeExtractionResult.input_id."
                    ),
                )
            )

        if (
            attribute_result.source_structuring_result_id
            != structuring_result.case_structuring_result_id
        ):
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="attribute_source_structuring_result_id_mismatch",
                    message=(
                        "AttributeExtractionResult.source_structuring_result_id "
                        "must match CaseStructuringResult.case_structuring_result_id."
                    ),
                )
            )

        if atomization_result.stage_id != structuring_result.stage_context.stage_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="stage_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.stage_id must match "
                        "CaseStructuringResult.stage_context.stage_id."
                    ),
                )
            )

        source_result_id = atomization_result.source_structuring_result_id
        expected_source_result_id = structuring_result.case_structuring_result_id
        if source_result_id is None:
            issues.append(
                _issue(
                    severity=ValidationSeverity.WARNING,
                    code="missing_source_structuring_result_id",
                    message=(
                        "EvidenceAtomizationResult.source_structuring_result_id "
                        "is missing, so exact upstream result identity cannot be "
                        "confirmed."
                    ),
                )
            )
        elif source_result_id != expected_source_result_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="source_structuring_result_id_mismatch",
                    message=(
                        "EvidenceAtomizationResult.source_structuring_result_id "
                        "must match CaseStructuringResult.case_structuring_result_id."
                    ),
                )
            )

        return issues

    def _validate_evidence_atom_sources(
        self,
        *,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        atomization_result: EvidenceAtomizationResult,
        items_by_id: dict[ItemID, StructuredClinicalItem],
    ) -> list[EvidenceAtomizationValidationIssue]:
        issues: list[EvidenceAtomizationValidationIssue] = []
        raw_text = structuring_result.input.raw_text
        attributes_by_id = {
            attribute.attribute_id: attribute
            for attribute in attribute_result.clinical_attributes
        }
        sections_by_id = {
            section.section_id: section
            for section in structuring_result.clinical_sections
        }

        for atom in atomization_result.evidence_atoms:
            source_items: list[StructuredClinicalItem] = []
            source_item_id_set = set(atom.source_item_ids)

            for item_id in atom.source_item_ids:
                item = items_by_id.get(item_id)
                if item is None:
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="missing_source_item",
                            message=(
                                "EvidenceAtom.source_item_ids must reference "
                                "existing StructuredClinicalItem.item_id values."
                            ),
                            related_item_id=item_id,
                            related_evidence_id=atom.evidence_id,
                        )
                    )
                    continue

                source_items.append(item)

            context_section_ids = {
                context.section_id
                for context in atom.source_contexts
            }
            source_item_section_ids = {
                item.section_id
                for item in source_items
            }

            if not atom.source_contexts:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="missing_source_context",
                        message="EvidenceAtom.source_contexts must not be empty.",
                        related_evidence_id=atom.evidence_id,
                    )
                )

            for context in atom.source_contexts:
                section = sections_by_id.get(context.section_id)
                if section is None:
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="source_context_section_not_found",
                            message=(
                                "EvidenceAtom.source_contexts.section_id must "
                                "reference an existing ClinicalSection.section_id."
                            ),
                            related_evidence_id=atom.evidence_id,
                        )
                    )
                    continue

                if _enum_value(context.section_type) != _enum_value(
                    section.section_type
                ):
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="source_context_section_type_mismatch",
                            message=(
                                "EvidenceAtom.source_contexts.section_type must "
                                "match the referenced ClinicalSection.section_type."
                            ),
                            related_evidence_id=atom.evidence_id,
                        )
                    )

                if (
                    source_item_section_ids
                    and context.section_id not in source_item_section_ids
                ):
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="source_context_without_source_item_section",
                            message=(
                                "EvidenceAtom.source_contexts entries must "
                                "correspond to sections referenced by the "
                                "atom's source_item_ids."
                            ),
                            related_evidence_id=atom.evidence_id,
                        )
                    )

            for item in source_items:
                if item.section_id in context_section_ids:
                    continue

                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="source_item_section_missing_from_context",
                        message=(
                            "Each EvidenceAtom.source_item_ids entry must have "
                            "its StructuredClinicalItem.section_id represented "
                            "in EvidenceAtom.source_contexts."
                        ),
                        related_item_id=item.item_id,
                        related_evidence_id=atom.evidence_id,
                    )
                )

            if len(source_item_section_ids) > 1:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.WARNING,
                        code="multi_section_evidence_atom",
                        message=(
                            "Evidence atom references multiple clinical sections; "
                            "check atom granularity."
                        ),
                        related_evidence_id=atom.evidence_id,
                    )
                )

            for attribute_id in atom.source_attribute_ids:
                attribute = attributes_by_id.get(attribute_id)
                if attribute is None:
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="missing_source_attribute",
                            message=(
                                "EvidenceAtom.source_attribute_ids must reference "
                                "existing ClinicalAttribute.attribute_id values."
                            ),
                            related_evidence_id=atom.evidence_id,
                            related_attribute_id=attribute_id,
                        )
                    )
                    continue

                if attribute.source_item_id not in source_item_id_set:
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="source_attribute_not_owned_by_source_item",
                            message=(
                                "EvidenceAtom.source_attribute_ids must belong to "
                                "one of the atom's source_item_ids."
                            ),
                            related_item_id=attribute.source_item_id,
                            related_evidence_id=atom.evidence_id,
                            related_attribute_id=attribute_id,
                        )
                    )

            spans_by_id = {
                span.span_id: span
                for item in source_items
                for span in item.source_spans
            }

            for span_id in atom.source_span_ids:
                if span_id in spans_by_id:
                    continue

                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="source_span_not_owned_by_source_item",
                        message=(
                            "EvidenceAtom.source_span_ids must reference spans "
                            "owned by the atom's source_item_ids."
                        ),
                        related_evidence_id=atom.evidence_id,
                        related_span_id=span_id,
                    )
                )

            referenced_span_texts = [
                spans_by_id[span_id].quoted_text
                for span_id in atom.source_span_ids
                if span_id in spans_by_id
            ]
            if _text_found_in_any(atom.source_text, referenced_span_texts):
                continue

            if _text_contains(raw_text, atom.source_text):
                issues.append(
                    _issue(
                        severity=ValidationSeverity.WARNING,
                        code="source_text_found_in_raw_text_but_not_referenced_span",
                        message=(
                            "EvidenceAtom.source_text was found in raw_text but "
                            "not in the referenced source span text. This may "
                            "indicate imprecise source_span_ids."
                        ),
                        related_evidence_id=atom.evidence_id,
                    )
                )
                continue

            issues.append(
                _issue(
                    severity=ValidationSeverity.WARNING,
                    code="source_text_not_found_in_source_span",
                    message=(
                        "EvidenceAtom.source_text was not found in referenced "
                        "source span text or raw_text after whitespace-normalized "
                        "matching."
                    ),
                    related_evidence_id=atom.evidence_id,
                )
            )

        return issues

    def _validate_item_evidence_links(
        self,
        *,
        atomization_result: EvidenceAtomizationResult,
        items_by_id: dict[ItemID, StructuredClinicalItem],
    ) -> list[EvidenceAtomizationValidationIssue]:
        issues: list[EvidenceAtomizationValidationIssue] = []

        for link in atomization_result.item_to_evidence_links:
            if link.item_id in items_by_id:
                continue

            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="link_item_not_found",
                    message=(
                        "ItemEvidenceLink.item_id must reference an existing "
                        "StructuredClinicalItem.item_id."
                    ),
                    related_item_id=link.item_id,
                )
            )

        return issues

    def _validate_deferred_items(
        self,
        *,
        atomization_result: EvidenceAtomizationResult,
        items_by_id: dict[ItemID, StructuredClinicalItem],
    ) -> list[EvidenceAtomizationValidationIssue]:
        issues: list[EvidenceAtomizationValidationIssue] = []

        for deferred_item in atomization_result.deferred_items:
            if deferred_item.item_id in items_by_id:
                continue

            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="deferred_item_not_found",
                    message=(
                        "DeferredStructuredItem.item_id must reference an "
                        "existing StructuredClinicalItem.item_id."
                    ),
                    related_item_id=deferred_item.item_id,
                )
            )

        return issues

    def _validate_item_coverage(
        self,
        *,
        structuring_result: CaseStructuringResult,
        atomization_result: EvidenceAtomizationResult,
    ) -> list[EvidenceAtomizationValidationIssue]:
        accounted_item_ids: set[ItemID] = set()

        for atom in atomization_result.evidence_atoms:
            accounted_item_ids.update(atom.source_item_ids)

        accounted_item_ids.update(
            link.item_id for link in atomization_result.item_to_evidence_links
        )
        accounted_item_ids.update(
            deferred_item.item_id for deferred_item in atomization_result.deferred_items
        )

        return [
            _issue(
                severity=ValidationSeverity.WARNING,
                code="structured_item_not_accounted_for",
                message=(
                    "StructuredClinicalItem is not referenced by any evidence "
                    "atom, item-evidence link, or deferred item."
                ),
                related_item_id=item.item_id,
            )
            for item in structuring_result.structured_items
            if item.item_id not in accounted_item_ids
        ]

    def _validate_deferred_link_consistency(
        self,
        atomization_result: EvidenceAtomizationResult,
    ) -> list[EvidenceAtomizationValidationIssue]:
        deferred_item_ids = {
            deferred_item.item_id for deferred_item in atomization_result.deferred_items
        }
        issues: list[EvidenceAtomizationValidationIssue] = []

        for link in atomization_result.item_to_evidence_links:
            if link.transformation_type != AtomizationTransformationType.DEFERRED:
                continue

            if link.item_id in deferred_item_ids:
                continue

            issues.append(
                _issue(
                    severity=ValidationSeverity.WARNING,
                    code="deferred_link_without_deferred_item",
                    message=(
                        "ItemEvidenceLink with transformation_type=deferred "
                        "should have a matching DeferredStructuredItem."
                    ),
                    related_item_id=link.item_id,
                )
            )

        return issues

    def _validate_possible_duplicate_atoms(
        self,
        atomization_result: EvidenceAtomizationResult,
    ) -> list[EvidenceAtomizationValidationIssue]:
        atom_ids_by_key: dict[tuple[object, ...], list[EvidenceID]] = defaultdict(list)

        for atom in atomization_result.evidence_atoms:
            key = (
                atom.statement,
                atom.normalized_label,
                tuple(sorted(atom.source_item_ids)),
                tuple(sorted(atom.source_attribute_ids)),
                atom.assertion_status,
                atom.temporality,
            )
            atom_ids_by_key[key].append(atom.evidence_id)

        issues: list[EvidenceAtomizationValidationIssue] = []
        for evidence_ids in atom_ids_by_key.values():
            if len(evidence_ids) < 2:
                continue

            for evidence_id in evidence_ids:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.WARNING,
                        code="possible_duplicate_evidence_atom",
                        message=(
                            "Multiple EvidenceAtom objects share the same "
                            "deterministic duplicate key."
                        ),
                        related_evidence_id=evidence_id,
                    )
                )

        return issues


def _structured_items_by_id(
    result: CaseStructuringResult,
) -> dict[ItemID, StructuredClinicalItem]:
    return {item.item_id: item for item in result.structured_items}


def _issue(
    *,
    severity: ValidationSeverity,
    code: str,
    message: str,
    related_item_id: ItemID | None = None,
    related_evidence_id: EvidenceID | None = None,
    related_span_id: SpanID | None = None,
    related_attribute_id: AttributeID | None = None,
) -> EvidenceAtomizationValidationIssue:
    return EvidenceAtomizationValidationIssue(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_evidence_id=related_evidence_id,
        related_span_id=related_span_id,
        related_attribute_id=related_attribute_id,
    )


def _text_found_in_any(needle: str, haystacks: list[str]) -> bool:
    return any(_text_contains(haystack, needle) for haystack in haystacks)


def _text_contains(haystack: str, needle: str) -> bool:
    if needle in haystack:
        return True

    normalized_needle = _normalize_text_for_match(needle)
    if not normalized_needle:
        return False

    return normalized_needle in _normalize_text_for_match(haystack)


def _normalize_text_for_match(text: str) -> str:
    return " ".join(text.split())


def _enum_value(value: object) -> object:
    return getattr(value, "value", value)
