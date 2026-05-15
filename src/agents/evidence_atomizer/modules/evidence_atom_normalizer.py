from __future__ import annotations

from collections import defaultdict
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_atomizer.atomization_warning import AtomizationWarning
from src.schemas.evidence_atomizer.common import (
    FORBIDDEN_REASONING_FIELD_NAMES,
    AtomizationTransformationType,
    CertaintyLevel,
    ClinicalDomain,
    ConfidenceLevel,
    DeferredReason,
    EvidenceGranularity,
    EvidenceType,
    NegationStatus,
    TemporalRelation,
    ValidationSeverity,
)
from src.schemas.evidence_atomizer.deferred_item import DeferredStructuredItem
from src.schemas.evidence_atomizer.evidence_atom import EvidenceAtom
from src.schemas.evidence_atomizer.item_evidence_link import ItemEvidenceLink

from .atomization_candidate_builder import AtomizationCandidate
from .coverage_units import CoverageUnit


class NormalizedEvidenceAtomizationPayload(BaseModel):
    """Formal schema objects normalized from an LLM draft payload."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    evidence_atoms: list[EvidenceAtom] = Field(default_factory=list)
    item_to_evidence_links: list[ItemEvidenceLink] = Field(default_factory=list)
    deferred_items: list[DeferredStructuredItem] = Field(default_factory=list)
    atomization_warnings: list[AtomizationWarning] = Field(default_factory=list)
    evidence_id_to_coverage_unit_ids: dict[str, list[str]] = Field(default_factory=dict)


class EvidenceAtomNormalizer:
    """Convert draft atomization payloads into formal schema objects."""

    def normalize(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        candidates: list[AtomizationCandidate],
        coverage_units: list[CoverageUnit],
        draft_payload: dict[str, Any],
    ) -> NormalizedEvidenceAtomizationPayload:
        context = _NormalizationContext(
            structuring_result,
            attribute_result,
            candidates,
            coverage_units,
        )
        warnings: list[AtomizationWarning] = []
        deferred_items: list[DeferredStructuredItem] = []
        evidence_atoms: list[EvidenceAtom] = []
        draft_id_to_evidence_id: dict[str, str] = {}
        evidence_id_to_coverage_unit_ids: dict[str, list[str]] = {}

        for index, draft in enumerate(_array(draft_payload, "evidence_atom_drafts"), start=1):
            if not isinstance(draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_evidence_atom_draft",
                        message="Evidence atom draft was not a JSON object.",
                    )
                )
                continue

            forbidden_fields = _find_forbidden_fields(draft) | (
                set(draft) & {"value", "unit", "body_site", "time_text"}
            )
            if forbidden_fields:
                source_item_ids = context.source_item_ids_from_payload(draft)
                warnings.append(
                    _warning(
                        code="downstream_reasoning_field_in_draft",
                        message=(
                            "Evidence atom draft contained downstream reasoning "
                            "fields and was deferred instead of atomized."
                        ),
                        related_item_id=source_item_ids[0] if source_item_ids else None,
                    )
                )
                deferred_items.extend(
                    context.defer_items(
                        source_item_ids,
                        DeferredReason.REQUIRES_DOWNSTREAM_INTERPRETATION,
                        "Draft contained downstream reasoning fields outside atomizer scope.",
                    )
                )
                continue

            source_item_ids = context.resolve_source_item_ids(draft)
            if not source_item_ids:
                warnings.append(
                    _warning(
                        code="missing_source_item_ids",
                        message=(
                            "Evidence atom draft had no clear source structured "
                            "item and was skipped."
                        ),
                    )
                )
                continue

            source_span_ids = context.resolve_source_span_ids(draft, source_item_ids)
            if not source_span_ids:
                warnings.append(
                    _warning(
                        code="missing_source_span_ids",
                        message=(
                            "Evidence atom draft could not be grounded to source "
                            "spans and was deferred."
                        ),
                        related_item_id=source_item_ids[0],
                    )
                )
                deferred_items.extend(
                    context.defer_items(
                        source_item_ids,
                        DeferredReason.INSUFFICIENT_SOURCE_SPAN,
                        "No source spans were available for safe atomization.",
                    )
                )
                continue

            source_attribute_ids = context.resolve_source_attribute_ids(
                draft,
                source_item_ids,
            )

            atom_payload = self._build_atom_payload(
                structuring_result=structuring_result,
                context=context,
                draft=draft,
                source_item_ids=source_item_ids,
                source_attribute_ids=source_attribute_ids,
                source_span_ids=source_span_ids,
                warnings=warnings,
            )
            try:
                atom = EvidenceAtom(**atom_payload)
            except (TypeError, ValueError, ValidationError):
                warnings.append(
                    _warning(
                        code="invalid_evidence_atom_draft",
                        message=(
                            "Evidence atom draft could not be normalized into a "
                            "valid EvidenceAtom."
                        ),
                        related_item_id=source_item_ids[0],
                    )
                )
                deferred_items.extend(
                    context.defer_items(
                        source_item_ids,
                        DeferredReason.TOO_AMBIGUOUS,
                        "Draft could not be normalized into a valid evidence atom.",
                    )
                )
                continue

            evidence_atoms.append(atom)
            evidence_id_to_coverage_unit_ids[atom.evidence_id] = (
                _coverage_unit_ids_from_draft(draft)
            )
            draft_ref = _draft_ref(draft, index)
            if draft_ref is not None:
                draft_id_to_evidence_id[draft_ref] = atom.evidence_id

        deferred_items.extend(
            self._normalize_deferred_items(
                context,
                _array(draft_payload, "deferred_items"),
                warnings,
            )
        )
        warnings.extend(
            self._normalize_warnings(_array(draft_payload, "atomization_warnings"))
        )

        item_to_evidence_ids: dict[str, list[str]] = defaultdict(list)
        for atom in evidence_atoms:
            for item_id in atom.source_item_ids:
                item_to_evidence_ids[item_id].append(atom.evidence_id)

        links = self._normalize_links(
            context=context,
            link_drafts=_array(draft_payload, "item_to_evidence_links"),
            draft_id_to_evidence_id=draft_id_to_evidence_id,
            item_to_evidence_ids=item_to_evidence_ids,
            deferred_items=deferred_items,
            warnings=warnings,
        )

        return NormalizedEvidenceAtomizationPayload(
            evidence_atoms=evidence_atoms,
            item_to_evidence_links=links,
            deferred_items=_dedupe_deferred_items(deferred_items),
            atomization_warnings=warnings,
            evidence_id_to_coverage_unit_ids=evidence_id_to_coverage_unit_ids,
        )

    def _build_atom_payload(
        self,
        *,
        structuring_result: CaseStructuringResult,
        context: "_NormalizationContext",
        draft: dict[str, Any],
        source_item_ids: list[str],
        source_attribute_ids: list[str],
        source_span_ids: list[str],
        warnings: list[AtomizationWarning],
    ) -> dict[str, Any]:
        source_items = [
            context.candidates_by_item_id[item_id]
            for item_id in source_item_ids
            if item_id in context.candidates_by_item_id
        ]
        primary = source_items[0] if source_items else None
        coverage_units = context.coverage_units_for_draft(draft)
        evidence_type_default = _evidence_type_default(primary)
        evidence_type = _coerce_enum(
            draft.get("evidence_type") or draft.get("type") or evidence_type_default,
            EvidenceType,
            EvidenceType.UNCERTAIN,
        )

        statement = _first_text(
            draft,
            ("statement", "evidence_statement", "normalized_statement", "label", "text"),
        )
        if statement is None and len(coverage_units) == 1:
            statement = coverage_units[0].surface_text
        if statement is None and primary is not None:
            statement = primary.label
        if statement is None:
            statement = context.source_text_for_spans(source_item_ids, source_span_ids)

        assertion_status = _resolve_assertion_status(
            draft=draft,
            coverage_units=coverage_units,
            source_items=source_items,
            warnings=warnings,
            related_item_id=source_item_ids[0] if source_item_ids else None,
        )

        return {
            "case_id": structuring_result.input.case_id,
            "input_id": structuring_result.input.input_id,
            "stage_id": structuring_result.stage_context.stage_id,
            "evidence_type": evidence_type,
            "clinical_domain": _coerce_enum(
                draft.get("clinical_domain") or _domain_default(evidence_type),
                ClinicalDomain,
                ClinicalDomain.UNCERTAIN,
            ),
            "granularity": _coerce_enum(
                draft.get("granularity"),
                EvidenceGranularity,
                EvidenceGranularity.ATOMIC,
            ),
            "statement": statement,
            "normalized_label": _optional_text(
                draft.get("normalized_label") or draft.get("label")
            ),
            "assertion_status": assertion_status,
            "certainty": _coerce_enum(
                draft.get("certainty"),
                CertaintyLevel,
                _shared_candidate_enum(source_items, "certainty", CertaintyLevel.UNKNOWN),
            ),
            "temporality": _coerce_enum(
                draft.get("temporality"),
                TemporalRelation,
                _shared_candidate_enum(
                    source_items,
                    "temporality",
                    TemporalRelation.UNKNOWN,
                ),
            ),
            "source_item_ids": source_item_ids,
            "source_attribute_ids": source_attribute_ids,
            "source_span_ids": source_span_ids,
            "source_text": _optional_text(draft.get("source_text"))
            or context.source_text_for_spans(source_item_ids, source_span_ids),
            "atomization_confidence": _coerce_enum(
                draft.get("atomization_confidence")
                or draft.get("confidence")
                or draft.get("classification_confidence"),
                ConfidenceLevel,
                ConfidenceLevel.MEDIUM,
            ),
            "notes": _optional_text(draft.get("notes")),
        }

    def _normalize_deferred_items(
        self,
        context: "_NormalizationContext",
        deferred_drafts: list[Any],
        warnings: list[AtomizationWarning],
    ) -> list[DeferredStructuredItem]:
        deferred_items: list[DeferredStructuredItem] = []
        for draft in deferred_drafts:
            if not isinstance(draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_deferred_item",
                        message="Deferred item draft was not a JSON object.",
                    )
                )
                continue

            source_item_ids = context.source_item_ids_from_payload(draft)
            if not source_item_ids:
                warnings.append(
                    _warning(
                        code="deferred_item_missing_item_id",
                        message="Deferred item draft did not reference a known item.",
                    )
                )
                continue

            reason = _coerce_enum(
                draft.get("reason"),
                DeferredReason,
                DeferredReason.TOO_AMBIGUOUS,
            )
            explanation = _optional_text(draft.get("explanation") or draft.get("message"))
            if explanation is None:
                explanation = "Structured item was deferred during atomization."

            for item_id in source_item_ids:
                span_ids = context.span_ids_for_item(item_id)
                item_reason = reason
                if not span_ids:
                    item_reason = DeferredReason.INSUFFICIENT_SOURCE_SPAN
                try:
                    deferred_items.append(
                        DeferredStructuredItem(
                            item_id=item_id,
                            reason=item_reason,
                            explanation=explanation,
                            related_span_ids=span_ids,
                        )
                    )
                except (TypeError, ValueError, ValidationError):
                    warnings.append(
                        _warning(
                            code="invalid_deferred_item",
                            message=(
                                "Deferred item draft could not be normalized "
                                "into a valid DeferredStructuredItem."
                            ),
                            related_item_id=item_id,
                        )
                    )

        return deferred_items

    def _normalize_warnings(
        self,
        warning_drafts: list[Any],
    ) -> list[AtomizationWarning]:
        warnings: list[AtomizationWarning] = []
        for draft in warning_drafts:
            if not isinstance(draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_atomization_warning",
                        message="Atomization warning draft was not a JSON object.",
                    )
                )
                continue

            warnings.append(
                _warning(
                    code=_optional_text(draft.get("code")) or "llm_atomization_warning",
                    message=_optional_text(draft.get("message"))
                    or "LLM reported an atomization warning.",
                    severity=_coerce_enum(
                        draft.get("severity"),
                        ValidationSeverity,
                        ValidationSeverity.WARNING,
                    ),
                    related_item_id=_optional_text(draft.get("related_item_id")),
                    related_evidence_id=_optional_text(draft.get("related_evidence_id")),
                    related_span_id=_optional_text(draft.get("related_span_id")),
                )
            )
        return warnings

    def _normalize_links(
        self,
        *,
        context: "_NormalizationContext",
        link_drafts: list[Any],
        draft_id_to_evidence_id: dict[str, str],
        item_to_evidence_ids: dict[str, list[str]],
        deferred_items: list[DeferredStructuredItem],
        warnings: list[AtomizationWarning],
    ) -> list[ItemEvidenceLink]:
        links_by_item_id: dict[str, ItemEvidenceLink] = {}

        for draft in link_drafts:
            if not isinstance(draft, dict):
                warnings.append(
                    _warning(
                        code="malformed_item_evidence_link",
                        message="Item-evidence link draft was not a JSON object.",
                    )
                )
                continue

            item_ids = context.source_item_ids_from_payload(draft)
            if not item_ids:
                warnings.append(
                    _warning(
                        code="link_missing_item_id",
                        message="Item-evidence link draft did not reference a known item.",
                    )
                )
                continue

            evidence_ids = _evidence_ids_from_link_draft(
                draft,
                draft_id_to_evidence_id,
            )
            transformation_type = _coerce_enum(
                draft.get("transformation_type"),
                AtomizationTransformationType,
                AtomizationTransformationType.COPIED,
            )
            explanation = _optional_text(draft.get("explanation"))

            for item_id in item_ids:
                merged_evidence_ids = _dedupe_strings(
                    evidence_ids + item_to_evidence_ids.get(item_id, [])
                )
                link = _safe_link(
                    item_id=item_id,
                    evidence_ids=merged_evidence_ids,
                    transformation_type=transformation_type,
                    explanation=explanation,
                    warnings=warnings,
                )
                if link is not None:
                    links_by_item_id[item_id] = link

        for item_id, evidence_ids in item_to_evidence_ids.items():
            if item_id in links_by_item_id:
                continue
            transformation_type = (
                AtomizationTransformationType.SPLIT
                if len(evidence_ids) > 1
                else AtomizationTransformationType.COPIED
            )
            links_by_item_id[item_id] = _safe_link(
                item_id=item_id,
                evidence_ids=evidence_ids,
                transformation_type=transformation_type,
                explanation=(
                    "Structured item was split into multiple evidence atoms."
                    if transformation_type == AtomizationTransformationType.SPLIT
                    else None
                ),
                warnings=warnings,
            )

        for deferred_item in deferred_items:
            if deferred_item.item_id in links_by_item_id:
                continue
            links_by_item_id[deferred_item.item_id] = _safe_link(
                item_id=deferred_item.item_id,
                evidence_ids=[],
                transformation_type=AtomizationTransformationType.DEFERRED,
                explanation=deferred_item.explanation,
                warnings=warnings,
            )

        return [
            link
            for _, link in sorted(
                links_by_item_id.items(),
                key=lambda pair: context.item_order(pair[0]),
            )
            if link is not None
        ]


class _NormalizationContext:
    def __init__(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
        candidates: list[AtomizationCandidate],
        coverage_units: list[CoverageUnit],
    ) -> None:
        self.structuring_result = structuring_result
        self.attribute_result = attribute_result
        self.candidates = candidates
        self.coverage_units = coverage_units
        self.candidates_by_item_id = {
            candidate.item_id: candidate
            for candidate in candidates
        }
        self.valid_item_ids = set(self.candidates_by_item_id)
        self.attributes_by_id = {
            attribute.attribute_id: attribute
            for attribute in attribute_result.clinical_attributes
        }
        self.coverage_units_by_id = {
            coverage_unit.unit_id: coverage_unit
            for coverage_unit in coverage_units
        }
        self._item_order = {
            item.item_id: item.item_order
            for item in structuring_result.structured_items
        }

    def item_order(self, item_id: str) -> int:
        return self._item_order.get(item_id, 10**9)

    def source_item_ids_from_payload(self, payload: dict[str, Any]) -> list[str]:
        values = _list_text(
            payload.get("source_item_ids")
            or payload.get("source_items")
            or payload.get("item_ids")
            or payload.get("item_id")
            or payload.get("source_item_id")
        )
        return _dedupe_strings(
            value for value in values if value in self.valid_item_ids
        )

    def resolve_source_item_ids(self, payload: dict[str, Any]) -> list[str]:
        source_item_ids = self.source_item_ids_from_payload(payload)
        if source_item_ids:
            return source_item_ids
        if len(self.candidates) == 1:
            return [self.candidates[0].item_id]
        return []

    def resolve_source_span_ids(
        self,
        payload: dict[str, Any],
        source_item_ids: list[str],
    ) -> list[str]:
        owned_span_ids = {
            span_id
            for item_id in source_item_ids
            for span_id in self.span_ids_for_item(item_id)
        }
        requested_span_ids = _list_text(
            payload.get("source_span_ids")
            or payload.get("span_ids")
            or payload.get("source_spans")
            or payload.get("source_span_id")
        )
        valid_requested = [
            span_id
            for span_id in requested_span_ids
            if span_id in owned_span_ids
        ]
        if valid_requested:
            return _dedupe_strings(valid_requested)
        return _dedupe_strings(
            span_id
            for item_id in source_item_ids
            for span_id in self.span_ids_for_item(item_id)
        )

    def resolve_source_attribute_ids(
        self,
        payload: dict[str, Any],
        source_item_ids: list[str],
    ) -> list[str]:
        source_item_id_set = set(source_item_ids)
        requested_attribute_ids = _list_text(
            payload.get("source_attribute_ids")
            or payload.get("attribute_ids")
            or payload.get("source_attributes")
            or payload.get("source_attribute_id")
        )
        valid_requested = [
            attribute_id
            for attribute_id in requested_attribute_ids
            if self.attribute_belongs_to_items(attribute_id, source_item_id_set)
        ]
        if valid_requested:
            return _dedupe_strings(valid_requested)

        coverage_attribute_ids: list[str] = []
        for coverage_unit_id in _coverage_unit_ids_from_draft(payload):
            coverage_unit = self.coverage_units_by_id.get(coverage_unit_id)
            if coverage_unit is None:
                continue
            coverage_attribute_ids.extend(coverage_unit.source_attribute_ids)
        return _dedupe_strings(
            attribute_id
            for attribute_id in coverage_attribute_ids
            if self.attribute_belongs_to_items(attribute_id, source_item_id_set)
        )

    def attribute_belongs_to_items(
        self,
        attribute_id: str,
        source_item_ids: set[str],
    ) -> bool:
        attribute = self.attributes_by_id.get(attribute_id)
        if attribute is None:
            return False
        return attribute.source_item_id in source_item_ids

    def span_ids_for_item(self, item_id: str) -> list[str]:
        candidate = self.candidates_by_item_id.get(item_id)
        if candidate is None:
            return []
        return [
            str(span["span_id"])
            for span in candidate.source_spans
            if isinstance(span.get("span_id"), str) and span["span_id"].strip()
        ]

    def source_text_for_spans(
        self,
        source_item_ids: list[str],
        source_span_ids: list[str],
    ) -> str:
        requested = set(source_span_ids)
        texts: list[str] = []
        for item_id in source_item_ids:
            candidate = self.candidates_by_item_id.get(item_id)
            if candidate is None:
                continue
            for span in candidate.source_spans:
                if span.get("span_id") not in requested:
                    continue
                quoted_text = span.get("quoted_text")
                if isinstance(quoted_text, str) and quoted_text.strip():
                    texts.append(quoted_text.strip())
        if texts:
            return "\n".join(_dedupe_strings(texts))
        return "\n".join(
            candidate.source_text
            for candidate in self.candidates
            if candidate.item_id in source_item_ids and candidate.source_text
        )

    def coverage_units_for_draft(
        self,
        payload: dict[str, Any],
    ) -> list[CoverageUnit]:
        units: list[CoverageUnit] = []
        for coverage_unit_id in _coverage_unit_ids_from_draft(payload):
            coverage_unit = self.coverage_units_by_id.get(coverage_unit_id)
            if coverage_unit is not None:
                units.append(coverage_unit)
        return units

    def defer_items(
        self,
        item_ids: list[str],
        reason: DeferredReason,
        explanation: str,
    ) -> list[DeferredStructuredItem]:
        deferred_items: list[DeferredStructuredItem] = []
        for item_id in item_ids:
            if item_id not in self.valid_item_ids:
                continue
            span_ids = self.span_ids_for_item(item_id)
            item_reason = reason if span_ids else DeferredReason.INSUFFICIENT_SOURCE_SPAN
            try:
                deferred_items.append(
                    DeferredStructuredItem(
                        item_id=item_id,
                        reason=item_reason,
                        explanation=explanation,
                        related_span_ids=span_ids,
                    )
                )
            except (TypeError, ValueError, ValidationError):
                continue
        return deferred_items


def _array(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    return value if isinstance(value, list) else []


def _first_text(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = _optional_text(payload.get(key))
        if value is not None:
            return value
    return None


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, StrEnum):
        value = value.value
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return None


def _list_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, dict):
        for key in (
            "item_id",
            "source_item_id",
            "span_id",
            "source_span_id",
            "attribute_id",
            "source_attribute_id",
            "coverage_unit_id",
            "id",
        ):
            text = _optional_text(value.get(key))
            if text is not None:
                return [text]
        return []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_list_text(item))
        return result
    return []


def _coerce_enum(value: Any, enum_type: type[StrEnum], default: StrEnum) -> StrEnum:
    allowed_values = {item.value: item for item in enum_type}
    if isinstance(value, enum_type):
        return value
    if isinstance(value, StrEnum):
        value = value.value
    if isinstance(value, str) and value in allowed_values:
        return allowed_values[value]
    return default


def _resolve_assertion_status(
    *,
    draft: dict[str, Any],
    coverage_units: list[CoverageUnit],
    source_items: list[AtomizationCandidate],
    warnings: list[AtomizationWarning],
    related_item_id: str | None,
) -> NegationStatus:
    coverage_assertion = _shared_coverage_unit_assertion_status(coverage_units)
    draft_assertion = _coerce_enum(
        draft.get("assertion_status") or draft.get("negation"),
        NegationStatus,
        _shared_candidate_enum(source_items, "negation", NegationStatus.UNKNOWN),
    )

    if coverage_assertion is None:
        return draft_assertion

    if draft_assertion != coverage_assertion:
        warnings.append(
            _warning(
                code="assertion_status_corrected_from_coverage_unit",
                message=(
                    "Evidence atom assertion_status was corrected to match the "
                    "assertion-aware coverage unit."
                ),
                related_item_id=related_item_id,
            )
        )
    return coverage_assertion


def _shared_coverage_unit_assertion_status(
    coverage_units: list[CoverageUnit],
) -> NegationStatus | None:
    raw_statuses = _dedupe_strings(
        _optional_text(coverage_unit.assertion_status)
        for coverage_unit in coverage_units
    )
    if not raw_statuses:
        return None
    if len(raw_statuses) > 1:
        return NegationStatus.UNKNOWN
    return _map_coverage_assertion_status(raw_statuses[0])


def _map_coverage_assertion_status(value: str | None) -> NegationStatus:
    if value == NegationStatus.PRESENT.value:
        return NegationStatus.PRESENT
    if value in {NegationStatus.ABSENT.value, NegationStatus.DENIED.value}:
        return NegationStatus.ABSENT
    if value in {
        NegationStatus.NOT_MENTIONED.value,
        NegationStatus.UNKNOWN.value,
        "possible",
        "uncertain",
    }:
        return NegationStatus.UNKNOWN
    return NegationStatus.UNKNOWN


def _shared_candidate_enum(
    candidates: list[AtomizationCandidate],
    attr_name: str,
    default: StrEnum,
) -> StrEnum:
    values = {
        value
        for candidate in candidates
        if (value := getattr(candidate, attr_name)) is not None
    }
    if len(values) == 1:
        return _coerce_enum(next(iter(values)), type(default), default)
    return default


def _evidence_type_default(candidate: AtomizationCandidate | None) -> EvidenceType:
    if candidate is None:
        return EvidenceType.UNCERTAIN
    return _coerce_enum(candidate.item_type, EvidenceType, EvidenceType.UNCERTAIN)


def _domain_default(evidence_type: EvidenceType) -> ClinicalDomain:
    mapping = {
        EvidenceType.SYMPTOM: ClinicalDomain.RESPIRATORY,
        EvidenceType.SIGN: ClinicalDomain.GENERAL,
        EvidenceType.LAB_RESULT: ClinicalDomain.LABORATORY,
        EvidenceType.IMAGING_FINDING: ClinicalDomain.RADIOLOGY,
        EvidenceType.PATHOLOGY_FINDING: ClinicalDomain.PATHOLOGY,
        EvidenceType.PULMONARY_FUNCTION: ClinicalDomain.PULMONARY_FUNCTION,
        EvidenceType.MEDICATION: ClinicalDomain.TREATMENT,
        EvidenceType.TREATMENT: ClinicalDomain.TREATMENT,
        EvidenceType.TREATMENT_RESPONSE: ClinicalDomain.TREATMENT,
        EvidenceType.EXPOSURE: ClinicalDomain.EXPOSURE_ENVIRONMENT,
        EvidenceType.SMOKING_HISTORY: ClinicalDomain.EXPOSURE_ENVIRONMENT,
    }
    return mapping.get(evidence_type, ClinicalDomain.GENERAL)


def _draft_ref(draft: dict[str, Any], index: int) -> str | None:
    return _optional_text(
        draft.get("draft_id")
        or draft.get("atom_id")
        or draft.get("temporary_id")
        or draft.get("id")
        or f"draft_{index:03d}"
    )


def _find_forbidden_fields(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_REASONING_FIELD_NAMES:
                found.add(key)
            found.update(_find_forbidden_fields(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_find_forbidden_fields(item))
    return found


def _evidence_ids_from_link_draft(
    draft: dict[str, Any],
    draft_id_to_evidence_id: dict[str, str],
) -> list[str]:
    values = _list_text(
        draft.get("evidence_ids")
        or draft.get("evidence_atom_ids")
        or draft.get("evidence_atom_draft_ids")
        or draft.get("atom_ids")
        or draft.get("draft_ids")
    )
    resolved = [draft_id_to_evidence_id.get(value, value) for value in values]
    return _dedupe_strings(resolved)


def _coverage_unit_ids_from_draft(draft: dict[str, Any]) -> list[str]:
    return _dedupe_strings(
        _list_text(
            draft.get("coverage_unit_ids")
            or draft.get("coverage_units")
            or draft.get("coverage_unit_id")
        )
    )


def _safe_link(
    *,
    item_id: str,
    evidence_ids: list[str],
    transformation_type: AtomizationTransformationType,
    explanation: str | None,
    warnings: list[AtomizationWarning],
) -> ItemEvidenceLink | None:
    if (
        transformation_type
        in {
            AtomizationTransformationType.SPLIT,
            AtomizationTransformationType.MERGED,
        }
        and explanation is None
    ):
        explanation = "Structured item required non-trivial atomization."

    if (
        transformation_type
        in {
            AtomizationTransformationType.DEFERRED,
            AtomizationTransformationType.DROPPED,
        }
        and explanation is None
    ):
        explanation = "Structured item did not produce evidence atoms."

    try:
        return ItemEvidenceLink(
            item_id=item_id,
            evidence_ids=_dedupe_strings(evidence_ids),
            transformation_type=transformation_type,
            explanation=explanation,
        )
    except (TypeError, ValueError, ValidationError):
        warnings.append(
            _warning(
                code="invalid_item_evidence_link",
                message=(
                    "Item-evidence link could not be normalized into a valid "
                    "ItemEvidenceLink."
                ),
                related_item_id=item_id,
            )
        )
        return None


def _warning(
    *,
    code: str,
    message: str,
    severity: ValidationSeverity = ValidationSeverity.WARNING,
    related_item_id: str | None = None,
    related_evidence_id: str | None = None,
    related_span_id: str | None = None,
) -> AtomizationWarning:
    try:
        return AtomizationWarning(
            severity=severity,
            code=code,
            message=message,
            related_item_id=related_item_id,
            related_evidence_id=related_evidence_id,
            related_span_id=related_span_id,
        )
    except (TypeError, ValueError, ValidationError):
        return AtomizationWarning(
            severity=severity,
            code="atomization_warning_normalization_failed",
            message="Atomization warning draft could not be normalized.",
            related_item_id=related_item_id,
            related_evidence_id=related_evidence_id,
            related_span_id=related_span_id,
        )


def _dedupe_strings(values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        text = _optional_text(value)
        if text is None or text in result:
            continue
        result.append(text)
    return result


def _dedupe_deferred_items(
    deferred_items: list[DeferredStructuredItem],
) -> list[DeferredStructuredItem]:
    seen: set[str] = set()
    result: list[DeferredStructuredItem] = []
    for item in deferred_items:
        if item.item_id in seen:
            continue
        seen.add(item.item_id)
        result.append(item)
    return result
