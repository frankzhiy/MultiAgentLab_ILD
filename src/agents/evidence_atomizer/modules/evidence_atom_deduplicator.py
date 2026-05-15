from __future__ import annotations

from src.schemas.evidence_atomizer.atomization_warning import AtomizationWarning
from src.schemas.evidence_atomizer.common import ValidationSeverity
from src.schemas.evidence_atomizer.evidence_atom import EvidenceAtom
from src.schemas.evidence_atomizer.item_evidence_link import ItemEvidenceLink

from .coverage_units import CoverageUnit
from .evidence_atom_normalizer import NormalizedEvidenceAtomizationPayload


class EvidenceAtomDeduplicator:
    """Remove duplicate or subsumed atoms using frame provenance."""

    def deduplicate(
        self,
        *,
        normalized_payload: NormalizedEvidenceAtomizationPayload,
        coverage_units: list[CoverageUnit],
    ) -> NormalizedEvidenceAtomizationPayload:
        coverage_units_by_id = {
            coverage_unit.unit_id: coverage_unit
            for coverage_unit in coverage_units
        }
        warnings = list(normalized_payload.atomization_warnings)
        atoms = list(normalized_payload.evidence_atoms)
        remove_ids: set[str] = set()

        remove_ids.update(
            self._exact_duplicates(
                atoms=atoms,
                warnings=warnings,
            )
        )
        remove_ids.update(
            self._same_local_duplicates(
                atoms=atoms,
                already_removed=remove_ids,
                warnings=warnings,
            )
        )
        remove_ids.update(
            self._subsumed_atoms(
                atoms=atoms,
                already_removed=remove_ids,
                evidence_id_to_coverage_unit_ids=(
                    normalized_payload.evidence_id_to_coverage_unit_ids
                ),
                coverage_units_by_id=coverage_units_by_id,
                warnings=warnings,
            )
        )

        if not remove_ids:
            return normalized_payload

        kept_atoms = [
            atom
            for atom in normalized_payload.evidence_atoms
            if atom.evidence_id not in remove_ids
        ]
        kept_links = _remove_atom_ids_from_links(
            normalized_payload.item_to_evidence_links,
            remove_ids,
        )
        kept_coverage = {
            evidence_id: coverage_unit_ids
            for evidence_id, coverage_unit_ids in (
                normalized_payload.evidence_id_to_coverage_unit_ids.items()
            )
            if evidence_id not in remove_ids
        }
        return normalized_payload.model_copy(
            update={
                "evidence_atoms": kept_atoms,
                "item_to_evidence_links": kept_links,
                "atomization_warnings": warnings,
                "evidence_id_to_coverage_unit_ids": kept_coverage,
            }
        )

    def _exact_duplicates(
        self,
        *,
        atoms: list[EvidenceAtom],
        warnings: list[AtomizationWarning],
    ) -> set[str]:
        seen: dict[tuple[tuple[str, ...], str, str], EvidenceAtom] = {}
        remove_ids: set[str] = set()
        for atom in atoms:
            key = (
                tuple(atom.source_item_ids),
                atom.assertion_status.value,
                _normalized_statement(atom.statement),
            )
            existing = seen.get(key)
            if existing is None:
                seen[key] = atom
                continue
            keep, remove = _more_context_complete(existing, atom)
            seen[key] = keep
            remove_ids.add(remove.evidence_id)
            warnings.append(
                _warning(
                    code="duplicate_evidence_atom_removed",
                    message="Exact duplicate EvidenceAtom was removed.",
                    related_item_id=atom.source_item_ids[0],
                    related_evidence_id=remove.evidence_id,
                )
            )
        return remove_ids

    def _same_local_duplicates(
        self,
        *,
        atoms: list[EvidenceAtom],
        already_removed: set[str],
        warnings: list[AtomizationWarning],
    ) -> set[str]:
        seen: dict[tuple[str, tuple[str, ...], str], EvidenceAtom] = {}
        remove_ids: set[str] = set()
        for atom in atoms:
            if atom.evidence_id in already_removed:
                continue
            local_content = (atom.local_content_text or "").strip()
            if not local_content:
                continue
            key = (
                local_content,
                tuple(atom.source_frame_node_ids),
                atom.assertion_status.value,
            )
            existing = seen.get(key)
            if existing is None:
                seen[key] = atom
                continue
            keep, remove = _more_context_complete(existing, atom)
            seen[key] = keep
            remove_ids.add(remove.evidence_id)
            warnings.append(
                _warning(
                    code="duplicate_evidence_atom_removed",
                    message="Duplicate EvidenceAtom with the same local frame content was removed.",
                    related_item_id=atom.source_item_ids[0],
                    related_evidence_id=remove.evidence_id,
                )
            )
        return remove_ids

    def _subsumed_atoms(
        self,
        *,
        atoms: list[EvidenceAtom],
        already_removed: set[str],
        evidence_id_to_coverage_unit_ids: dict[str, list[str]],
        coverage_units_by_id: dict[str, CoverageUnit],
        warnings: list[AtomizationWarning],
    ) -> set[str]:
        remove_ids: set[str] = set()
        active_atoms = [
            atom for atom in atoms if atom.evidence_id not in already_removed
        ]
        for index, left in enumerate(active_atoms):
            for right in active_atoms[index + 1 :]:
                if left.evidence_id in remove_ids or right.evidence_id in remove_ids:
                    continue
                if not _same_subsumption_scope(left, right):
                    if _possible_granularity_conflict(left, right):
                        warnings.append(
                            _warning(
                                code="possible_granularity_conflict",
                                message="Overlapping EvidenceAtoms share a frame parent but have different structural provenance, so both were kept.",
                                related_item_id=left.source_item_ids[0],
                            )
                        )
                    continue
                if _sibling_property_pair(left, right):
                    continue
                if _has_group_modifier_policy(
                    left,
                    right,
                    evidence_id_to_coverage_unit_ids,
                    coverage_units_by_id,
                ):
                    warnings.append(
                        _warning(
                            code="group_modifier_overlap",
                            message="Group modifier EvidenceAtom overlaps another atom but was kept by policy.",
                            related_item_id=left.source_item_ids[0],
                        )
                    )
                    continue

                left_statement = _normalized_statement(left.statement)
                right_statement = _normalized_statement(right.statement)
                if left_statement == right_statement:
                    continue
                if left_statement and left_statement in right_statement:
                    remove = left
                elif right_statement and right_statement in left_statement:
                    remove = right
                else:
                    continue
                remove_ids.add(remove.evidence_id)
                warnings.append(
                    _warning(
                        code="subsumed_evidence_atom_removed",
                        message="Shorter EvidenceAtom was subsumed by a context-complete atom under the same frame parent.",
                        related_item_id=remove.source_item_ids[0],
                        related_evidence_id=remove.evidence_id,
                    )
                )

        return remove_ids


def _same_subsumption_scope(left: EvidenceAtom, right: EvidenceAtom) -> bool:
    if left.source_item_ids != right.source_item_ids:
        return False
    if left.assertion_status != right.assertion_status:
        return False
    if not set(left.parent_frame_node_ids) & set(right.parent_frame_node_ids):
        return False
    if left.source_frame_node_ids != right.source_frame_node_ids:
        return False
    return True


def _possible_granularity_conflict(left: EvidenceAtom, right: EvidenceAtom) -> bool:
    if left.source_item_ids != right.source_item_ids:
        return False
    if left.assertion_status != right.assertion_status:
        return False
    if not set(left.parent_frame_node_ids) & set(right.parent_frame_node_ids):
        return False
    left_statement = _normalized_statement(left.statement)
    right_statement = _normalized_statement(right.statement)
    return bool(
        left_statement
        and right_statement
        and (
            left_statement in right_statement
            or right_statement in left_statement
        )
    )


def _sibling_property_pair(left: EvidenceAtom, right: EvidenceAtom) -> bool:
    return bool(
        set(left.parent_frame_node_ids) & set(right.parent_frame_node_ids)
        and set(left.source_frame_node_ids) != set(right.source_frame_node_ids)
        and left.local_content_text
        and right.local_content_text
        and left.local_content_text != right.local_content_text
    )


def _has_group_modifier_policy(
    left: EvidenceAtom,
    right: EvidenceAtom,
    evidence_id_to_coverage_unit_ids: dict[str, list[str]],
    coverage_units_by_id: dict[str, CoverageUnit],
) -> bool:
    for atom in (left, right):
        for coverage_unit_id in evidence_id_to_coverage_unit_ids.get(atom.evidence_id, []):
            coverage_unit = coverage_units_by_id.get(coverage_unit_id)
            if (
                coverage_unit is not None
                and coverage_unit.atomization_policy == "generate_group_modifier_atom"
            ):
                return True
    return False


def _more_context_complete(
    left: EvidenceAtom,
    right: EvidenceAtom,
) -> tuple[EvidenceAtom, EvidenceAtom]:
    left_score = _context_score(left)
    right_score = _context_score(right)
    if right_score > left_score:
        return right, left
    return left, right


def _context_score(atom: EvidenceAtom) -> tuple[int, int, int]:
    return (
        len(atom.context_frame_node_ids),
        len(atom.atom_context_text or ""),
        len(atom.statement),
    )


def _normalized_statement(statement: str) -> str:
    return "".join(statement.split())


def _remove_atom_ids_from_links(
    links: list[ItemEvidenceLink],
    remove_ids: set[str],
) -> list[ItemEvidenceLink]:
    result: list[ItemEvidenceLink] = []
    for link in links:
        evidence_ids = [
            evidence_id
            for evidence_id in link.evidence_ids
            if evidence_id not in remove_ids
        ]
        result.append(link.model_copy(update={"evidence_ids": evidence_ids}))
    return result


def _warning(
    *,
    code: str,
    message: str,
    related_item_id: str | None = None,
    related_evidence_id: str | None = None,
    severity: ValidationSeverity = ValidationSeverity.WARNING,
) -> AtomizationWarning:
    return AtomizationWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_evidence_id=related_evidence_id,
    )
