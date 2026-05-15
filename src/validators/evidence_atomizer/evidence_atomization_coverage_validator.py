"""Deterministic coverage validation for Evidence Atomizer output."""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.agents.evidence_atomizer.modules.coverage_units import CoverageUnit
from src.schemas.evidence_atomizer.common import (
    EvidenceID,
    ItemID,
    ValidationSeverity,
    normalize_optional_text,
    require_non_empty_text,
)
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)


class EvidenceAtomizationCoverageIssue(BaseModel):
    """One deterministic atomization coverage issue."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    related_item_id: ItemID | None = None
    related_evidence_id: EvidenceID | None = None
    related_coverage_unit_id: str | None = None

    @field_validator("code", "message", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "Required text fields")

    @field_validator(
        "related_item_id",
        "related_evidence_id",
        "related_coverage_unit_id",
        mode="after",
    )
    @classmethod
    def optional_ids_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)


class CoverageValidationResult(BaseModel):
    """Internal validation result for EvidenceAtom coverage of CoverageUnit objects."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    accepted: bool
    issues: list[EvidenceAtomizationCoverageIssue] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    @model_validator(mode="after")
    def validate_acceptance_matches_errors(
        self,
    ) -> "CoverageValidationResult":
        expected_accepted = not self.has_errors
        if self.accepted != expected_accepted:
            raise ValueError(
                "accepted must be True only when there are no ERROR issues."
            )
        return self


class EvidenceAtomizationCoverageValidator:
    """Validate deterministic CoverageUnit coverage without clinical reasoning."""

    def validate(
        self,
        *,
        coverage_units: list[CoverageUnit],
        evidence_id_to_coverage_unit_ids: dict[str, list[str]],
        atomization_result: EvidenceAtomizationResult,
    ) -> CoverageValidationResult:
        issues: list[EvidenceAtomizationCoverageIssue] = []
        coverage_units_by_id = {
            coverage_unit.unit_id: coverage_unit
            for coverage_unit in coverage_units
        }
        evidence_atoms_by_id = {
            atom.evidence_id: atom
            for atom in atomization_result.evidence_atoms
        }
        required_units = [
            coverage_unit
            for coverage_unit in coverage_units
            if coverage_unit.required
        ]

        if required_units and not atomization_result.evidence_atoms:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="no_evidence_atoms_for_required_coverage",
                    message=(
                        "EvidenceAtomizationResult contains no EvidenceAtoms "
                        "while required coverage units exist."
                    ),
                )
            )

        unit_to_evidence_ids: dict[str, list[str]] = defaultdict(list)
        for evidence_id, coverage_unit_ids in evidence_id_to_coverage_unit_ids.items():
            unique_coverage_unit_ids = _dedupe_strings(coverage_unit_ids)

            if len(unique_coverage_unit_ids) > 1:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.WARNING,
                        code="evidence_atom_covers_multiple_units",
                        message=(
                            "One EvidenceAtom should normally cover exactly one "
                            "CoverageUnit."
                        ),
                        related_evidence_id=evidence_id,
                    )
                )

            for coverage_unit_id in unique_coverage_unit_ids:
                if coverage_unit_id not in coverage_units_by_id:
                    issues.append(
                        _issue(
                            severity=ValidationSeverity.ERROR,
                            code="unknown_coverage_unit_id",
                            message=(
                                "EvidenceAtom referenced a coverage_unit_id that "
                                "does not exist."
                            ),
                            related_evidence_id=evidence_id,
                            related_coverage_unit_id=coverage_unit_id,
                        )
                    )
                    continue

                unit_to_evidence_ids[coverage_unit_id].append(evidence_id)
                atom = evidence_atoms_by_id.get(evidence_id)
                if atom is not None:
                    issues.extend(
                        _assertion_consistency_issues(
                            atom_assertion_status=_atom_assertion_label(
                                getattr(atom.assertion_status, "value", atom.assertion_status)
                            ),
                            coverage_unit=coverage_units_by_id[coverage_unit_id],
                            related_evidence_id=evidence_id,
                        )
                    )

        for coverage_unit in required_units:
            evidence_ids = unit_to_evidence_ids.get(coverage_unit.unit_id, [])
            if evidence_ids:
                continue

            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="coverage_unit_not_covered",
                    message=(
                        "Required CoverageUnit must be referenced by at least "
                        "one EvidenceAtom."
                    ),
                    related_item_id=coverage_unit.source_item_id,
                    related_coverage_unit_id=coverage_unit.unit_id,
                )
            )

        for coverage_unit_id, evidence_ids in sorted(unit_to_evidence_ids.items()):
            unique_evidence_ids = _dedupe_strings(evidence_ids)
            if len(unique_evidence_ids) <= 1:
                continue

            coverage_unit = coverage_units_by_id[coverage_unit_id]
            issues.append(
                _issue(
                    severity=ValidationSeverity.WARNING,
                    code="coverage_unit_covered_multiple_times",
                    message=(
                        "One CoverageUnit should normally be covered by exactly "
                        "one EvidenceAtom."
                    ),
                    related_item_id=coverage_unit.source_item_id,
                    related_coverage_unit_id=coverage_unit_id,
                )
            )

        for atom in atomization_result.evidence_atoms:
            issues.extend(
                _statement_assertion_issues(
                    statement=atom.statement,
                    assertion_status=_atom_assertion_label(
                        getattr(atom.assertion_status, "value", atom.assertion_status)
                    ),
                    related_evidence_id=atom.evidence_id,
                )
            )

        return CoverageValidationResult(
            accepted=not any(
                issue.severity == ValidationSeverity.ERROR for issue in issues
            ),
            issues=issues,
        )


def _issue(
    *,
    severity: ValidationSeverity,
    code: str,
    message: str,
    related_item_id: ItemID | None = None,
    related_evidence_id: EvidenceID | None = None,
    related_coverage_unit_id: str | None = None,
) -> EvidenceAtomizationCoverageIssue:
    return EvidenceAtomizationCoverageIssue(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_evidence_id=related_evidence_id,
        related_coverage_unit_id=related_coverage_unit_id,
    )


def _dedupe_strings(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        cleaned = normalize_optional_text(value)
        if cleaned is None or cleaned in result:
            continue
        result.append(cleaned)
    return result


def _assertion_consistency_issues(
    *,
    atom_assertion_status: str,
    coverage_unit: CoverageUnit,
    related_evidence_id: str,
) -> list[EvidenceAtomizationCoverageIssue]:
    coverage_assertion_status = _coverage_assertion_label(coverage_unit.assertion_status)
    if coverage_assertion_status == atom_assertion_status:
        return []

    severity = (
        ValidationSeverity.ERROR
        if {atom_assertion_status, coverage_assertion_status} == {"present", "absent"}
        else ValidationSeverity.WARNING
    )
    return [
        _issue(
            severity=severity,
            code="coverage_unit_assertion_status_mismatch",
            message=(
                "EvidenceAtom assertion_status conflicted with its assertion-aware "
                "CoverageUnit."
            ),
            related_item_id=coverage_unit.source_item_id,
            related_evidence_id=related_evidence_id,
            related_coverage_unit_id=coverage_unit.unit_id,
        )
    ]


def _statement_assertion_issues(
    *,
    statement: str,
    assertion_status: str,
    related_evidence_id: str,
) -> list[EvidenceAtomizationCoverageIssue]:
    negation_prefixes = ("未见", "未诉", "否认", "不伴", "无", "未")
    positive_cues = ("再次出现", "出现", "伴")
    compact_statement = " ".join(statement.split())

    if (
        assertion_status == "present"
        and compact_statement.startswith(negation_prefixes)
        and not any(cue in compact_statement for cue in positive_cues)
    ):
        return [
            _issue(
                severity=ValidationSeverity.WARNING,
                code="present_atom_has_negation_surface",
                message=(
                    "EvidenceAtom statement begins with a negation expression while "
                    "assertion_status is present."
                ),
                related_evidence_id=related_evidence_id,
            )
        ]

    if (
        assertion_status == "absent"
        and any(cue in compact_statement for cue in positive_cues)
        and not compact_statement.startswith(negation_prefixes)
    ):
        return [
            _issue(
                severity=ValidationSeverity.WARNING,
                code="absent_atom_has_positive_surface",
                message=(
                    "EvidenceAtom statement contains a positive cue while "
                    "assertion_status is absent."
                ),
                related_evidence_id=related_evidence_id,
            )
        ]

    return []


def _coverage_assertion_label(value: str | None) -> str:
    normalized = normalize_optional_text(value) or "unknown"
    if normalized in {"absent", "denied"}:
        return "absent"
    if normalized == "present":
        return "present"
    return "unknown"


def _atom_assertion_label(value: str | None) -> str:
    normalized = normalize_optional_text(value) or "unknown"
    if normalized in {"absent", "denied"}:
        return "absent"
    if normalized == "present":
        return "present"
    return "unknown"
