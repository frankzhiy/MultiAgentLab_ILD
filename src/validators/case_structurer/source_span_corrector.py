"""Deterministic source-span correction for Case Structurer output."""

from __future__ import annotations

from itertools import product
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.validators.case_structurer.source_span_utils import (
    SourceRange,
    cjk_chunks,
    find_resolvable_span_pieces,
    find_all_occurrences,
    offsets_in_bounds,
    range_inside_any_parent,
    range_distance,
    required_alnum_tokens,
    resolved_range,
    valid_ranges,
)
from src.validators.case_structurer.source_span_validator import (
    ItemSourceSpanValidator,
    SectionSourceSpanValidator,
    SourceSpanValidationReport,
)


class SourceSpanCorrectionAction(BaseModel):
    """One deterministic correction attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: str = Field(description="Either applied or skipped.")
    code: str
    message: str
    object_type: str
    object_id: str
    span_id: str | None = None
    field_name: str | None = None
    before_quoted_text: str | None = None
    after_quoted_text: str | None = None


class SourceSpanCorrectionReport(BaseModel):
    """Report of source-span corrections that were applied or skipped."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    actions: list[SourceSpanCorrectionAction] = Field(default_factory=list)
    applied_count: int = 0
    skipped_count: int = 0


class SectionSourceSpanValidationCorrectionResult(BaseModel):
    """Section-stage validation and correction output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    initial_sections: list[ClinicalSection]
    corrected_sections: list[ClinicalSection]
    initial_validation_report: SourceSpanValidationReport
    correction_report: SourceSpanCorrectionReport
    final_validation_report: SourceSpanValidationReport


class ItemSourceSpanValidationCorrectionResult(BaseModel):
    """Item-stage validation and correction output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    initial_items: list[StructuredClinicalItem]
    corrected_items: list[StructuredClinicalItem]
    initial_validation_report: SourceSpanValidationReport
    correction_report: SourceSpanCorrectionReport
    final_validation_report: SourceSpanValidationReport


class CaseStructuringSourceSpanResult(BaseModel):
    """Case Structurer output with separate section and item span reports."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    corrected_result: CaseStructuringResult
    section_span_result: SectionSourceSpanValidationCorrectionResult
    item_span_result: ItemSourceSpanValidationCorrectionResult


class SectionSourceSpanCorrector:
    """Correct ClinicalSection provenance fields without changing content."""

    def correct(
        self,
        sections: Sequence[ClinicalSection],
        raw_text: str,
        expected_input_id: str,
    ) -> tuple[list[ClinicalSection], SourceSpanCorrectionReport]:
        actions: list[SourceSpanCorrectionAction] = []
        corrected_sections = self._correct_sections(
            sections=sections,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            actions=actions,
        )
        return corrected_sections, _build_report(actions)

    def _correct_sections(
        self,
        sections: Sequence[ClinicalSection],
        raw_text: str,
        expected_input_id: str,
        actions: list[SourceSpanCorrectionAction],
    ) -> list[ClinicalSection]:
        corrected: list[ClinicalSection] = []
        for section in sections:
            spans = _correct_object_spans(
                object_type="ClinicalSection",
                object_id=section.section_id,
                source_spans=section.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=[section.title],
                preferred_ranges=[(0, len(raw_text))],
                allow_discontinuous_split=True,
                actions=actions,
            )
            corrected.append(
                _rebuild_object(
                    section,
                    {"input_id": expected_input_id, "source_spans": spans},
                    actions,
                    object_type="ClinicalSection",
                    object_id=section.section_id,
                )
            )
        return corrected


class ItemSourceSpanCorrector:
    """Correct StructuredClinicalItem provenance fields within sections."""

    def correct(
        self,
        items: Sequence[StructuredClinicalItem],
        raw_text: str,
        expected_input_id: str,
        sections: Sequence[ClinicalSection],
    ) -> tuple[list[StructuredClinicalItem], SourceSpanCorrectionReport]:
        actions: list[SourceSpanCorrectionAction] = []
        ranges_by_section = _section_ranges_from_sections(sections, raw_text)
        section_ids = {section.section_id for section in sections}
        corrected = self._correct_items(
            items=items,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            ranges_by_section=ranges_by_section,
            section_ids=section_ids,
            actions=actions,
        )
        return corrected, _build_report(actions)

    def _correct_items(
        self,
        items: Sequence[StructuredClinicalItem],
        raw_text: str,
        expected_input_id: str,
        ranges_by_section: dict[str, list[SourceRange]],
        section_ids: set[str],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[StructuredClinicalItem]:
        corrected: list[StructuredClinicalItem] = []
        for item in items:
            if item.section_id not in section_ids:
                _record(
                    actions,
                    status="skipped",
                    code="item_parent_section_not_found",
                    message=(
                        "Could not correct item source spans because the parent "
                        "ClinicalSection does not exist."
                    ),
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                )
                corrected.append(item)
                continue

            parent_ranges = ranges_by_section.get(item.section_id, [])
            spans = _correct_object_spans(
                object_type="StructuredClinicalItem",
                object_id=item.item_id,
                source_spans=item.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=[],
                preferred_ranges=parent_ranges,
                allow_discontinuous_split=False,
                actions=actions,
            )
            spans = _correct_item_parent_range(
                item=item,
                spans=spans,
                raw_text=raw_text,
                parent_ranges=parent_ranges,
                actions=actions,
            )
            corrected.append(
                _rebuild_object(
                    item,
                    {"input_id": expected_input_id, "source_spans": spans},
                    actions,
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                )
            )
        return corrected


def _correct_object_spans(
    object_type: str,
    object_id: str,
    source_spans: Sequence[SourceSpan],
    raw_text: str,
    expected_input_id: str,
    support_values: Sequence[str | None],
    preferred_ranges: Sequence[SourceRange],
    allow_discontinuous_split: bool,
    actions: list[SourceSpanCorrectionAction],
) -> list[SourceSpan]:
    spans = list(source_spans)
    if not spans:
        new_span = _span_from_support_values(
            object_type=object_type,
            object_id=object_id,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            support_values=support_values,
            preferred_ranges=preferred_ranges,
            actions=actions,
        )
        return [new_span] if new_span is not None else spans

    corrected_spans: list[SourceSpan] = []
    for span in spans:
        if allow_discontinuous_split and not quoted_text_exactly_found(
            raw_text, span.quoted_text
        ):
            split_spans = _split_discontinuous_span(
                object_type=object_type,
                object_id=object_id,
                span=span,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                preferred_ranges=preferred_ranges,
                actions=actions,
            )
            if split_spans:
                corrected_spans.extend(split_spans)
                continue

        corrected_spans.append(
            _correct_single_span(
                object_type=object_type,
                object_id=object_id,
                span=span,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=support_values,
                preferred_ranges=preferred_ranges,
                actions=actions,
            )
        )
    return corrected_spans


def _correct_single_span(
    object_type: str,
    object_id: str,
    span: SourceSpan,
    raw_text: str,
    expected_input_id: str,
    support_values: Sequence[str | None],
    preferred_ranges: Sequence[SourceRange],
    actions: list[SourceSpanCorrectionAction],
) -> SourceSpan:
    updated_span = span

    if updated_span.input_id != expected_input_id:
        updated_span = updated_span.model_copy(update={"input_id": expected_input_id})
        _record(
            actions,
            status="applied",
            code="source_span_input_id_mismatch",
            message="Corrected SourceSpan.input_id to result.input.input_id.",
            object_type=object_type,
            object_id=object_id,
            span_id=span.span_id,
            before_quoted_text=span.quoted_text,
            after_quoted_text=updated_span.quoted_text,
        )

    resolved = _resolve_exact_range(
        raw_text=raw_text,
        quoted_text=updated_span.quoted_text,
        preferred_ranges=preferred_ranges,
    )
    if resolved is not None:
        start, end = resolved
        if (
            updated_span.char_start != start
            or updated_span.char_end != end
            or not span_slice_safe(raw_text, updated_span)
        ):
            correction_code = _offset_correction_code(raw_text, updated_span)
            current_range = resolved_range(updated_span, raw_text)
            if (
                object_type == "StructuredClinicalItem"
                and preferred_ranges
                and current_range is not None
                and not range_inside_any_parent(current_range, preferred_ranges)
                and range_inside_any_parent((start, end), preferred_ranges)
            ):
                correction_code = "item_span_outside_parent_section"
            updated_span = updated_span.model_copy(
                update={"char_start": start, "char_end": end}
            )
            _record(
                actions,
                status="applied",
                code=correction_code,
                message="Recomputed SourceSpan character offsets.",
                object_type=object_type,
                object_id=object_id,
                span_id=span.span_id,
                before_quoted_text=span.quoted_text,
                after_quoted_text=updated_span.quoted_text,
            )
        return updated_span

    repaired_range = _best_support_range(
        raw_text=raw_text,
        values=support_values,
        preferred_ranges=preferred_ranges,
    )
    if repaired_range is None:
        _record(
            actions,
            status="skipped",
            code="quoted_text_not_found",
            message="Could not deterministically replace missing quoted_text.",
            object_type=object_type,
            object_id=object_id,
            span_id=span.span_id,
            before_quoted_text=span.quoted_text,
            after_quoted_text=None,
        )
        return updated_span.model_copy(update={"char_start": None, "char_end": None})

    start, end = repaired_range
    quoted_text = raw_text[start:end]
    _record(
        actions,
        status="applied",
        code="quoted_text_not_found",
        message="Replaced missing quoted_text with a deterministic raw_text span.",
        object_type=object_type,
        object_id=object_id,
        span_id=span.span_id,
        before_quoted_text=span.quoted_text,
        after_quoted_text=quoted_text,
    )
    return updated_span.model_copy(
        update={"quoted_text": quoted_text, "char_start": start, "char_end": end}
    )


def _split_discontinuous_span(
    object_type: str,
    object_id: str,
    span: SourceSpan,
    raw_text: str,
    expected_input_id: str,
    preferred_ranges: Sequence[SourceRange],
    actions: list[SourceSpanCorrectionAction],
) -> list[SourceSpan]:
    piece_ranges = find_resolvable_span_pieces(
        raw_text=raw_text,
        quoted_text=span.quoted_text,
        ranges=preferred_ranges,
    )
    if len(piece_ranges) < 2:
        return []

    split_spans = [
        SourceSpan(
            span_id=f"{span.span_id}_part_{index:03d}",
            input_id=expected_input_id,
            quoted_text=raw_text[start:end],
            char_start=start,
            char_end=end,
        )
        for index, (start, end) in enumerate(piece_ranges, start=1)
    ]
    _record(
        actions,
        status="applied",
        code="section_quoted_text_discontinuous_or_synthetic",
        message="Split synthetic section quoted_text into exact raw_text spans.",
        object_type=object_type,
        object_id=object_id,
        span_id=span.span_id,
        before_quoted_text=span.quoted_text,
        after_quoted_text=" ".join(split_span.quoted_text for split_span in split_spans),
    )
    return split_spans


def _correct_item_parent_range(
    item: StructuredClinicalItem,
    spans: Sequence[SourceSpan],
    raw_text: str,
    parent_ranges: Sequence[SourceRange],
    actions: list[SourceSpanCorrectionAction],
) -> list[SourceSpan]:
    if not parent_ranges:
        return list(spans)

    corrected: list[SourceSpan] = []
    for span in spans:
        span_range = resolved_range(span, raw_text)
        if span_range is None or range_inside_any_parent(span_range, parent_ranges):
            corrected.append(span)
            continue

        parent_occurrence = _resolve_exact_range(
            raw_text=raw_text,
            quoted_text=span.quoted_text,
            preferred_ranges=parent_ranges,
        )
        if parent_occurrence is None or not range_inside_any_parent(
            parent_occurrence, parent_ranges
        ):
            _record(
                actions,
                status="skipped",
                code="item_span_outside_parent_section",
                message=(
                    "Could not move item source span inside parent section "
                    "because quoted_text was not found there."
                ),
                object_type="StructuredClinicalItem",
                object_id=item.item_id,
                span_id=span.span_id,
                before_quoted_text=span.quoted_text,
                after_quoted_text=None,
            )
            corrected.append(span)
            continue

        start, end = parent_occurrence
        corrected_span = span.model_copy(update={"char_start": start, "char_end": end})
        _record(
            actions,
            status="applied",
            code="item_span_outside_parent_section",
            message="Moved item source span to the matching parent section range.",
            object_type="StructuredClinicalItem",
            object_id=item.item_id,
            span_id=span.span_id,
            before_quoted_text=span.quoted_text,
            after_quoted_text=corrected_span.quoted_text,
        )
        corrected.append(corrected_span)
    return corrected


def _span_from_support_values(
    object_type: str,
    object_id: str,
    raw_text: str,
    expected_input_id: str,
    support_values: Sequence[str | None],
    preferred_ranges: Sequence[SourceRange],
    actions: list[SourceSpanCorrectionAction],
) -> SourceSpan | None:
    support_range = _best_support_range(
        raw_text=raw_text,
        values=support_values,
        preferred_ranges=preferred_ranges,
    )
    if support_range is None:
        _record(
            actions,
            status="skipped",
            code="missing_source_span",
            message="Could not deterministically create a source span.",
            object_type=object_type,
            object_id=object_id,
        )
        return None

    start, end = support_range
    quoted_text = raw_text[start:end]
    span = SourceSpan(
        span_id=f"span_{object_id}_corrected_001",
        input_id=expected_input_id,
        quoted_text=quoted_text,
        char_start=start,
        char_end=end,
    )
    _record(
        actions,
        status="applied",
        code="missing_source_span",
        message="Created a deterministic source span.",
        object_type=object_type,
        object_id=object_id,
        span_id=span.span_id,
        after_quoted_text=quoted_text,
    )
    return span


def _offset_correction_code(raw_text: str, span: SourceSpan) -> str:
    if span.char_start is None or span.char_end is None:
        return "unresolved_offsets"
    if not offsets_in_bounds(raw_text, span.char_start, span.char_end):
        return "char_offsets_out_of_bounds"
    if not span_slice_safe(raw_text, span):
        return "char_offsets_do_not_match_quoted_text"
    return "source_span_offsets_recomputed"


def quoted_text_exactly_found(raw_text: str, quoted_text: str) -> bool:
    return bool(quoted_text) and quoted_text in raw_text


def validate_and_correct_section_spans(
    raw_text: str,
    expected_input_id: str,
    sections: Sequence[ClinicalSection],
    validator: SectionSourceSpanValidator | None = None,
    corrector: SectionSourceSpanCorrector | None = None,
) -> SectionSourceSpanValidationCorrectionResult:
    """Run section-only source-span validation, correction, then validation."""
    validator = validator or SectionSourceSpanValidator()
    corrector = corrector or SectionSourceSpanCorrector()

    initial_report = validator.validate(
        raw_text=raw_text,
        expected_input_id=expected_input_id,
        sections=sections,
    )
    corrected_sections, correction_report = corrector.correct(
        sections=sections,
        raw_text=raw_text,
        expected_input_id=expected_input_id,
    )
    final_report = validator.validate(
        raw_text=raw_text,
        expected_input_id=expected_input_id,
        sections=corrected_sections,
    )
    return SectionSourceSpanValidationCorrectionResult(
        initial_sections=list(sections),
        corrected_sections=corrected_sections,
        initial_validation_report=initial_report,
        correction_report=correction_report,
        final_validation_report=final_report,
    )


def validate_and_correct_item_spans(
    raw_text: str,
    expected_input_id: str,
    sections: Sequence[ClinicalSection],
    items: Sequence[StructuredClinicalItem],
    validator: ItemSourceSpanValidator | None = None,
    corrector: ItemSourceSpanCorrector | None = None,
) -> ItemSourceSpanValidationCorrectionResult:
    """Run item-only source-span validation, correction, then validation."""
    validator = validator or ItemSourceSpanValidator()
    corrector = corrector or ItemSourceSpanCorrector()

    initial_report = validator.validate(
        raw_text=raw_text,
        expected_input_id=expected_input_id,
        sections=sections,
        items=items,
    )
    corrected_items, correction_report = corrector.correct(
        items=items,
        raw_text=raw_text,
        expected_input_id=expected_input_id,
        sections=sections,
    )
    final_report = validator.validate(
        raw_text=raw_text,
        expected_input_id=expected_input_id,
        sections=sections,
        items=corrected_items,
    )
    return ItemSourceSpanValidationCorrectionResult(
        initial_items=list(items),
        corrected_items=corrected_items,
        initial_validation_report=initial_report,
        correction_report=correction_report,
        final_validation_report=final_report,
    )


def span_slice_safe(raw_text: str, span: SourceSpan) -> bool:
    if span.char_start is None or span.char_end is None:
        return False
    if not offsets_in_bounds(raw_text, span.char_start, span.char_end):
        return False
    return raw_text[span.char_start : span.char_end] == span.quoted_text


def _resolve_exact_range(
    raw_text: str,
    quoted_text: str,
    preferred_ranges: Sequence[SourceRange],
) -> SourceRange | None:
    if not quoted_text:
        return None

    ranges = list(preferred_ranges or [(0, len(raw_text))])
    preferred_occurrences = find_all_occurrences(raw_text, quoted_text, ranges)
    if preferred_occurrences:
        return preferred_occurrences[0]

    global_occurrences = find_all_occurrences(raw_text, quoted_text)
    if not global_occurrences:
        return None

    if preferred_ranges:
        return min(
            global_occurrences,
            key=lambda occurrence: (
                min(range_distance(occurrence, preferred) for preferred in ranges),
                occurrence[0],
                occurrence[1],
            ),
        )

    return global_occurrences[0]


def _best_support_range(
    raw_text: str,
    values: Sequence[str | None],
    preferred_ranges: Sequence[SourceRange],
) -> SourceRange | None:
    cleaned_values = [value.strip() for value in values if value and value.strip()]
    if not cleaned_values:
        return None

    ranges = valid_ranges(raw_text, preferred_ranges or [(0, len(raw_text))])
    if not ranges:
        ranges = [(0, len(raw_text))]

    if len(cleaned_values) == 1:
        occurrences = find_all_occurrences(raw_text, cleaned_values[0], ranges)
        if len(occurrences) == 1:
            return occurrences[0]
    else:
        primary_occurrences = find_all_occurrences(raw_text, cleaned_values[0], ranges)
        if len(primary_occurrences) == 1:
            return primary_occurrences[0]

    pieces = _support_pieces(raw_text, cleaned_values, ranges)
    if not pieces:
        return None

    occurrence_lists = [find_all_occurrences(raw_text, piece, ranges) for piece in pieces]
    if any(not occurrences for occurrences in occurrence_lists):
        return None

    total_combinations = 1
    for occurrences in occurrence_lists:
        total_combinations *= len(occurrences)
        if total_combinations > 10000:
            return _best_greedy_support_range(occurrence_lists)

    best_range: SourceRange | None = None
    best_key: tuple[int, int, int] | None = None
    ambiguous = False
    for combination in product(*occurrence_lists):
        start = min(item[0] for item in combination)
        end = max(item[1] for item in combination)
        key = (end - start, start, end)
        if best_key is None or key < best_key:
            best_key = key
            best_range = (start, end)
            ambiguous = False
        elif key[0] == best_key[0] and (start, end) != best_range:
            ambiguous = True

    if ambiguous:
        return None
    return best_range


def _best_greedy_support_range(
    occurrence_lists: Sequence[Sequence[SourceRange]],
) -> SourceRange | None:
    best_range: SourceRange | None = None
    best_key: tuple[int, int, int] | None = None

    for anchor in occurrence_lists[0]:
        selected = [anchor]
        current_start, current_end = anchor
        for occurrences in occurrence_lists[1:]:
            chosen = min(
                occurrences,
                key=lambda occurrence: range_distance(
                    occurrence,
                    (current_start, current_end),
                ),
            )
            selected.append(chosen)
            current_start = min(current_start, chosen[0])
            current_end = max(current_end, chosen[1])

        key = (current_end - current_start, current_start, current_end)
        if best_key is None or key < best_key:
            best_key = key
            best_range = (current_start, current_end)

    return best_range


def _support_pieces(
    raw_text: str,
    values: Sequence[str],
    ranges: Sequence[SourceRange],
) -> list[str]:
    pieces: list[str] = []
    for value in values:
        if find_all_occurrences(raw_text, value, ranges):
            pieces.append(value)
            continue

        pieces.extend(cjk_chunks(value))
        pieces.extend(required_alnum_tokens(value))

    return _dedupe_nonblank(pieces)


def _section_ranges_from_sections(
    sections: Sequence[ClinicalSection],
    raw_text: str,
) -> dict[str, list[SourceRange]]:
    ranges: dict[str, list[SourceRange]] = {}
    for section in sections:
        for span in section.source_spans:
            span_range = resolved_range(span, raw_text)
            if span_range is not None:
                ranges.setdefault(section.section_id, []).append(span_range)
    return ranges


def _rebuild_object(
    model: Any,
    updates: dict[str, Any],
    actions: list[SourceSpanCorrectionAction],
    object_type: str,
    object_id: str,
) -> Any:
    data = model.model_dump(mode="python")
    data.update(updates)
    try:
        return type(model).model_validate(data)
    except ValidationError as exc:
        _record(
            actions,
            status="skipped",
            code="schema_validation_failed",
            message=f"Skipped object corrections because schema validation failed: {exc}",
            object_type=object_type,
            object_id=object_id,
        )
        return model


def _record(
    actions: list[SourceSpanCorrectionAction],
    *,
    status: str,
    code: str,
    message: str,
    object_type: str,
    object_id: str,
    span_id: str | None = None,
    field_name: str | None = None,
    before_quoted_text: str | None = None,
    after_quoted_text: str | None = None,
) -> None:
    actions.append(
        SourceSpanCorrectionAction(
            status=status,
            code=code,
            message=message,
            object_type=object_type,
            object_id=object_id,
            span_id=span_id,
            field_name=field_name,
            before_quoted_text=before_quoted_text,
            after_quoted_text=after_quoted_text,
        )
    )


def _build_report(
    actions: list[SourceSpanCorrectionAction],
) -> SourceSpanCorrectionReport:
    applied_count = sum(1 for action in actions if action.status == "applied")
    skipped_count = sum(1 for action in actions if action.status == "skipped")
    return SourceSpanCorrectionReport(
        actions=actions,
        applied_count=applied_count,
        skipped_count=skipped_count,
    )


def _dedupe_nonblank(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        deduped.append(cleaned)
    return deduped
