"""Deterministic source-span correction for Case Structurer output."""

from __future__ import annotations

from itertools import product
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent
from src.validators.case_structurer.source_span_utils import (
    SourceRange,
    cjk_chunks,
    combined_existing_span_text,
    find_all_occurrences,
    item_field_supported_by_source,
    item_field_values,
    normalize_text_for_match,
    offsets_in_bounds,
    range_distance,
    required_alnum_tokens,
    resolved_range,
    span_slice_matches,
    unsupported_item_fields,
    valid_ranges,
)
from src.validators.case_structurer.source_span_validator import (
    SourceSpanValidationIssue,
    SourceSpanValidationReport,
    StrictSourceSpanValidator,
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


class SourceSpanValidationCorrectionResult(BaseModel):
    """Bundle output for validation, correction, and final residual issues."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    initial_result: CaseStructuringResult
    corrected_result: CaseStructuringResult
    initial_validation_report: SourceSpanValidationReport
    correction_report: SourceSpanCorrectionReport
    final_validation_report: SourceSpanValidationReport
    residual_issues: list[SourceSpanValidationIssue] = Field(default_factory=list)


class DeterministicSourceSpanCorrector:
    """Correct provenance fields without changing clinical meaning."""

    def correct(
        self,
        result: CaseStructuringResult,
        initial_validation_report: SourceSpanValidationReport | None = None,
    ) -> tuple[CaseStructuringResult, SourceSpanCorrectionReport]:
        """Return a corrected result plus a correction report."""
        del initial_validation_report
        actions: list[SourceSpanCorrectionAction] = []
        raw_text = result.input.raw_text
        expected_input_id = result.input.input_id

        corrected_sections = self._correct_sections(
            sections=result.clinical_sections,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            actions=actions,
        )

        ranges_by_section = _section_ranges_from_sections(corrected_sections, raw_text)

        corrected_items = self._correct_items(
            items=result.structured_items,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            ranges_by_section=ranges_by_section,
            actions=actions,
        )

        item_ranges = _item_range_map(corrected_items, raw_text)

        corrected_events = self._correct_timeline_events(
            events=result.timeline_events,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            item_ranges=item_ranges,
            actions=actions,
        )

        corrected_ambiguities = self._correct_ambiguities(
            ambiguities=result.ambiguities,
            raw_text=raw_text,
            expected_input_id=expected_input_id,
            ranges_by_section=ranges_by_section,
            item_ranges=item_ranges,
            actions=actions,
        )

        corrected_result = _rebuild_result(
            result,
            clinical_sections=corrected_sections,
            structured_items=corrected_items,
            timeline_events=corrected_events,
            ambiguities=corrected_ambiguities,
        )
        report = _build_report(actions)
        return corrected_result, report

    def _correct_sections(
        self,
        sections: Sequence[ClinicalSection],
        raw_text: str,
        expected_input_id: str,
        actions: list[SourceSpanCorrectionAction],
    ) -> list[ClinicalSection]:
        corrected: list[ClinicalSection] = []
        for section in sections:
            spans = self._correct_object_spans(
                object_type="ClinicalSection",
                object_id=section.section_id,
                source_spans=section.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=[section.normalized_text, section.title],
                preferred_ranges=[(0, len(raw_text))],
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

    def _correct_items(
        self,
        items: Sequence[StructuredClinicalItem],
        raw_text: str,
        expected_input_id: str,
        ranges_by_section: dict[str, list[SourceRange]],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[StructuredClinicalItem]:
        corrected: list[StructuredClinicalItem] = []
        for item in items:
            parent_ranges = ranges_by_section.get(item.section_id, [])
            spans = self._correct_object_spans(
                object_type="StructuredClinicalItem",
                object_id=item.item_id,
                source_spans=item.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=list(item_field_values(item).values()),
                preferred_ranges=parent_ranges,
                actions=actions,
            )
            spans = self._add_missing_item_support_spans(
                item=item,
                spans=spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                preferred_ranges=parent_ranges,
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

    def _correct_timeline_events(
        self,
        events: Sequence[TimelineEvent],
        raw_text: str,
        expected_input_id: str,
        item_ranges: dict[str, list[SourceRange]],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[TimelineEvent]:
        corrected: list[TimelineEvent] = []
        for event in events:
            preferred_ranges = _extend_ranges(event.related_item_ids, item_ranges)
            spans = self._correct_object_spans(
                object_type="TimelineEvent",
                object_id=event.event_id,
                source_spans=event.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=[event.description, event.event_time_text],
                preferred_ranges=preferred_ranges,
                actions=actions,
            )
            corrected.append(
                _rebuild_object(
                    event,
                    {"input_id": expected_input_id, "source_spans": spans},
                    actions,
                    object_type="TimelineEvent",
                    object_id=event.event_id,
                )
            )
        return corrected

    def _correct_ambiguities(
        self,
        ambiguities: Sequence[AmbiguityItem],
        raw_text: str,
        expected_input_id: str,
        ranges_by_section: dict[str, list[SourceRange]],
        item_ranges: dict[str, list[SourceRange]],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[AmbiguityItem]:
        corrected: list[AmbiguityItem] = []
        for ambiguity in ambiguities:
            preferred_ranges = _extend_ranges(ambiguity.related_item_ids, item_ranges)
            preferred_ranges.extend(
                _extend_ranges(ambiguity.related_section_ids, ranges_by_section)
            )
            spans = self._correct_object_spans(
                object_type="AmbiguityItem",
                object_id=ambiguity.ambiguity_id,
                source_spans=ambiguity.source_spans,
                raw_text=raw_text,
                expected_input_id=expected_input_id,
                support_values=[ambiguity.ambiguous_text],
                preferred_ranges=preferred_ranges,
                actions=actions,
            )
            corrected.append(
                _rebuild_object(
                    ambiguity,
                    {"input_id": expected_input_id, "source_spans": spans},
                    actions,
                    object_type="AmbiguityItem",
                    object_id=ambiguity.ambiguity_id,
                )
            )
        return corrected

    def _correct_object_spans(
        self,
        object_type: str,
        object_id: str,
        source_spans: Sequence[SourceSpan],
        raw_text: str,
        expected_input_id: str,
        support_values: Sequence[str | None],
        preferred_ranges: Sequence[SourceRange],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[SourceSpan]:
        spans = list(source_spans)
        if not spans:
            new_span = self._span_from_support_values(
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
            corrected_spans.append(
                self._correct_single_span(
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
        self,
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
            updated_span = updated_span.model_copy(
                update={"input_id": expected_input_id}
            )
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
                updated_span = updated_span.model_copy(
                    update={"char_start": start, "char_end": end}
                )
                _record(
                    actions,
                    status="applied",
                    code="source_span_offsets_recomputed",
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

    def _span_from_support_values(
        self,
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

    def _add_missing_item_support_spans(
        self,
        item: StructuredClinicalItem,
        spans: list[SourceSpan],
        raw_text: str,
        expected_input_id: str,
        preferred_ranges: Sequence[SourceRange],
        actions: list[SourceSpanCorrectionAction],
    ) -> list[SourceSpan]:
        source_text = combined_existing_span_text(raw_text, spans)
        unsupported_fields = unsupported_item_fields(item, source_text)
        if not unsupported_fields:
            return spans

        corrected_spans = list(spans)
        for field_name in unsupported_fields:
            value = item_field_values(item).get(field_name)
            if value is None:
                continue

            missing_values = _missing_support_values(
                field_name=field_name,
                value=value,
                source_text=combined_existing_span_text(raw_text, corrected_spans),
                raw_text=raw_text,
                preferred_ranges=preferred_ranges,
            )
            if not missing_values:
                _record(
                    actions,
                    status="skipped",
                    code="item_source_span_insufficient_support",
                    message="Could not identify a missing field-support span.",
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                    field_name=field_name,
                )
                continue

            for missing_value in missing_values:
                support_range = _best_support_range(
                    raw_text=raw_text,
                    values=[missing_value],
                    preferred_ranges=preferred_ranges,
                )
                if support_range is None:
                    _record(
                        actions,
                        status="skipped",
                        code="item_source_span_insufficient_support",
                        message="Missing field support was not uniquely locatable.",
                        object_type="StructuredClinicalItem",
                        object_id=item.item_id,
                        field_name=field_name,
                        before_quoted_text=missing_value,
                    )
                    continue

                start, end = support_range
                quoted_text = raw_text[start:end]
                new_span = SourceSpan(
                    span_id=(
                        f"span_{item.item_id}_{field_name}_support_"
                        f"{len(corrected_spans) + 1:03d}"
                    ),
                    input_id=expected_input_id,
                    quoted_text=quoted_text,
                    char_start=start,
                    char_end=end,
                )
                if _has_equivalent_span(corrected_spans, new_span):
                    continue

                corrected_spans.append(new_span)
                _record(
                    actions,
                    status="applied",
                    code="item_source_span_insufficient_support",
                    message="Added minimal source span for unsupported item field.",
                    object_type="StructuredClinicalItem",
                    object_id=item.item_id,
                    span_id=new_span.span_id,
                    field_name=field_name,
                    after_quoted_text=quoted_text,
                )

        return corrected_spans


def validate_and_correct_source_spans(
    result: CaseStructuringResult,
    validator: StrictSourceSpanValidator | None = None,
    corrector: DeterministicSourceSpanCorrector | None = None,
) -> SourceSpanValidationCorrectionResult:
    """Run validation, deterministic correction, and validation again."""
    validator = validator or StrictSourceSpanValidator()
    corrector = corrector or DeterministicSourceSpanCorrector()

    initial_report = validator.validate(result)
    corrected_result, correction_report = corrector.correct(
        result,
        initial_validation_report=initial_report,
    )
    final_report = validator.validate(corrected_result)
    residual_issues = list(final_report.issues)

    return SourceSpanValidationCorrectionResult(
        initial_result=result,
        corrected_result=corrected_result,
        initial_validation_report=initial_report,
        correction_report=correction_report,
        final_validation_report=final_report,
        residual_issues=residual_issues,
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


def _missing_support_values(
    field_name: str,
    value: str,
    source_text: str,
    raw_text: str,
    preferred_ranges: Sequence[SourceRange],
) -> list[str]:
    if item_field_supported_by_source(field_name, value, source_text):
        return []

    cleaned = value.strip()
    if not cleaned:
        return []

    if not normalize_text_for_match(cleaned).lower() in normalize_text_for_match(
        source_text
    ).lower() and find_all_occurrences(raw_text, cleaned, preferred_ranges):
        return [cleaned]

    missing: list[str] = []
    normalized_source = normalize_text_for_match(source_text).lower()
    for chunk in cjk_chunks(cleaned):
        if chunk not in source_text:
            missing.append(chunk)
    for token in required_alnum_tokens(cleaned):
        if token.lower() not in normalized_source:
            missing.append(token)

    return _dedupe_nonblank(missing)


def _has_equivalent_span(spans: Sequence[SourceSpan], candidate: SourceSpan) -> bool:
    candidate_range = (candidate.char_start, candidate.char_end)
    for span in spans:
        if span.quoted_text == candidate.quoted_text:
            return True
        if (span.char_start, span.char_end) == candidate_range:
            return True
    return False


def _item_range_map(
    items: Sequence[StructuredClinicalItem],
    raw_text: str,
) -> dict[str, list[SourceRange]]:
    ranges: dict[str, list[SourceRange]] = {}
    for item in items:
        for span in item.source_spans:
            span_range = resolved_range(span, raw_text)
            if span_range is not None:
                ranges.setdefault(item.item_id, []).append(span_range)
    return ranges


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


def _extend_ranges(
    object_ids: Sequence[str],
    range_map: dict[str, list[SourceRange]],
) -> list[SourceRange]:
    ranges: list[SourceRange] = []
    for object_id in object_ids:
        ranges.extend(range_map.get(object_id, []))
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


def _rebuild_result(
    result: CaseStructuringResult,
    **updates: Any,
) -> CaseStructuringResult:
    data = result.model_dump(mode="python")
    data.update(updates)
    try:
        return CaseStructuringResult.model_validate(data)
    except ValidationError:
        return result.model_copy(update=updates)


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
