from __future__ import annotations

from dataclasses import dataclass

from src.schemas.case_structurer.ambiguity_item import AmbiguityItem
from src.schemas.case_structurer.clinical_section import ClinicalSection
from src.schemas.case_structurer.raw_text_input import RawTextInput
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem
from src.schemas.case_structurer.timeline_event import TimelineEvent

SourceRange = tuple[int, int]


@dataclass(frozen=True)
class ResolvedSourceObjects:
    sections: list[ClinicalSection]
    items: list[StructuredClinicalItem]
    timeline_events: list[TimelineEvent]
    ambiguities: list[AmbiguityItem]


def _find_all_occurrences(text: str, query: str) -> list[SourceRange]:
    """Return all exact query occurrences, including overlapping matches."""
    if not query:
        return []

    occurrences: list[SourceRange] = []
    cursor = 0
    while True:
        start = text.find(query, cursor)
        if start < 0:
            break

        end = start + len(query)
        occurrences.append((start, end))
        cursor = start + 1

    return occurrences


def _valid_ranges(text: str, ranges: list[SourceRange]) -> list[SourceRange]:
    text_length = len(text)
    valid_ranges: list[SourceRange] = []
    for start, end in ranges:
        bounded_start = max(0, start)
        bounded_end = min(text_length, end)
        if bounded_start < bounded_end:
            valid_ranges.append((bounded_start, bounded_end))

    return valid_ranges


def _find_occurrence_within_ranges(
    text: str,
    query: str,
    ranges: list[SourceRange],
) -> SourceRange | None:
    """Find the first exact occurrence inside the caller's ordered ranges."""
    if not query:
        return None

    for range_start, range_end in _valid_ranges(text, ranges):
        start = text.find(query, range_start, range_end)
        if start >= 0:
            return (start, start + len(query))

    return None


def _range_distance(left: SourceRange, right: SourceRange) -> int:
    left_start, left_end = left
    right_start, right_end = right

    if left_end < right_start:
        return right_start - left_end
    if right_end < left_start:
        return left_start - right_end
    return 0


def _choose_nearest_occurrence(
    occurrences: list[SourceRange],
    preferred_ranges: list[SourceRange],
) -> SourceRange | None:
    """Choose the exact occurrence closest to any preferred context range."""
    if not occurrences or not preferred_ranges:
        return None

    usable_ranges = [
        (start, end) for start, end in preferred_ranges if start <= end
    ]
    if not usable_ranges:
        return None

    return min(
        occurrences,
        key=lambda occurrence: (
            min(_range_distance(occurrence, preferred) for preferred in usable_ranges),
            occurrence[0],
            occurrence[1],
        ),
    )


def _resolve_span(
    span: SourceSpan,
    raw_input: RawTextInput,
    preferred_ranges: list[SourceRange] | None = None,
    fallback_ranges: list[SourceRange] | None = None,
    span_id: str | None = None,
) -> SourceSpan:
    """Resolve a SourceSpan by exact match, preferring local context first."""
    text = raw_input.raw_text
    query = span.quoted_text
    preferred_ranges = preferred_ranges or []
    fallback_ranges = fallback_ranges or []

    resolved_range = _find_occurrence_within_ranges(text, query, preferred_ranges)
    if resolved_range is None:
        resolved_range = _find_occurrence_within_ranges(text, query, fallback_ranges)

    occurrences: list[SourceRange] | None = None
    if resolved_range is None:
        occurrences = _find_all_occurrences(text, query)
        resolved_range = _choose_nearest_occurrence(occurrences, preferred_ranges)

    if resolved_range is None:
        if occurrences is None:
            occurrences = _find_all_occurrences(text, query)
        if occurrences:
            resolved_range = occurrences[0]

    if resolved_range is None:
        char_start: int | None = None
        char_end: int | None = None
    else:
        char_start, char_end = resolved_range

    resolved_span_id = span.span_id
    if not str(resolved_span_id).strip() and span_id is not None:
        resolved_span_id = span_id

    return span.model_copy(
        update={
            "span_id": resolved_span_id,
            "input_id": raw_input.input_id,
            "char_start": char_start,
            "char_end": char_end,
        }
    )


def _resolved_range(span: SourceSpan) -> SourceRange | None:
    if span.char_start is None or span.char_end is None:
        return None

    return (span.char_start, span.char_end)


def _extend_ranges_for_ids(
    object_ids: list[str],
    range_map: dict[str, list[SourceRange]],
) -> list[SourceRange]:
    ranges: list[SourceRange] = []
    for object_id in object_ids:
        ranges.extend(range_map.get(object_id, []))

    return ranges


class SourceSpanResolver:
    """Resolve exact quoted_text offsets against the raw input."""

    def resolve(
        self,
        raw_input: RawTextInput,
        sections: list[ClinicalSection],
        items: list[StructuredClinicalItem],
        timeline_events: list[TimelineEvent],
        ambiguities: list[AmbiguityItem],
    ) -> ResolvedSourceObjects:
        span_counter = 0

        def resolve_single_span(
            span: SourceSpan,
            preferred_ranges: list[SourceRange] | None = None,
            fallback_ranges: list[SourceRange] | None = None,
        ) -> SourceSpan:
            nonlocal span_counter
            span_counter += 1
            span_id = None
            if not str(span.span_id).strip():
                span_id = f"span_{span_counter:03d}"

            return _resolve_span(
                span=span,
                raw_input=raw_input,
                preferred_ranges=preferred_ranges,
                fallback_ranges=fallback_ranges,
                span_id=span_id,
            )

        # ClinicalSection spans are resolved first because they provide the
        # parent text ranges used to anchor every more specific object below.
        section_range_map: dict[str, list[SourceRange]] = {}
        resolved_sections_by_index: dict[int, ClinicalSection] = {}
        section_cursor = 0

        sections_in_text_order = sorted(
            enumerate(sections),
            key=lambda indexed_section: (
                indexed_section[1].section_order,
                indexed_section[0],
            ),
        )
        for section_index, section in sections_in_text_order:
            resolved_spans: list[SourceSpan] = []
            for span in section.source_spans:
                resolved_span = resolve_single_span(
                    span,
                    preferred_ranges=[(section_cursor, len(raw_input.raw_text))],
                )
                resolved_spans.append(resolved_span)

                span_range = _resolved_range(resolved_span)
                if span_range is not None:
                    section_range_map.setdefault(section.section_id, []).append(
                        span_range
                    )
                    section_cursor = max(section_cursor, span_range[1])

            resolved_sections_by_index[section_index] = section.model_copy(
                update={"source_spans": resolved_spans}
            )

        resolved_sections = [
            resolved_sections_by_index[index] for index in range(len(sections))
        ]

        # StructuredClinicalItem spans should resolve inside their parent section
        # first. This prevents repeated quoted_text from being mapped to an
        # earlier global occurrence in a different clinical section.
        item_range_map: dict[str, list[SourceRange]] = {}
        item_section_id_map: dict[str, str] = {}
        resolved_items: list[StructuredClinicalItem] = []
        for item in items:
            item_section_id_map[item.item_id] = item.section_id
            parent_section_ranges = section_range_map.get(item.section_id, [])
            resolved_spans = [
                resolve_single_span(span, preferred_ranges=parent_section_ranges)
                for span in item.source_spans
            ]

            for resolved_span in resolved_spans:
                span_range = _resolved_range(resolved_span)
                if span_range is not None:
                    item_range_map.setdefault(item.item_id, []).append(span_range)

            resolved_items.append(
                item.model_copy(update={"source_spans": resolved_spans})
            )

        def parent_section_ranges_for_item_ids(item_ids: list[str]) -> list[SourceRange]:
            ranges: list[SourceRange] = []
            for item_id in item_ids:
                section_id = item_section_id_map.get(item_id)
                if section_id is not None:
                    ranges.extend(section_range_map.get(section_id, []))

            return ranges

        # TimelineEvent spans use related item ranges first, then their parent
        # section ranges. This keeps event provenance near the clinical fact it
        # references while still staying exact-match only.
        resolved_timeline_events: list[TimelineEvent] = []
        for event in timeline_events:
            related_item_ranges = _extend_ranges_for_ids(
                event.related_item_ids,
                item_range_map,
            )
            related_section_ranges = parent_section_ranges_for_item_ids(
                event.related_item_ids
            )
            resolved_spans = [
                resolve_single_span(
                    span,
                    preferred_ranges=related_item_ranges,
                    fallback_ranges=related_section_ranges,
                )
                for span in event.source_spans
            ]
            resolved_timeline_events.append(
                event.model_copy(update={"source_spans": resolved_spans})
            )

        # AmbiguityItem spans use related item and section ids as context. This
        # avoids forcing ambiguous repeated text back to the first global match.
        resolved_ambiguities: list[AmbiguityItem] = []
        for ambiguity in ambiguities:
            preferred_ranges = _extend_ranges_for_ids(
                ambiguity.related_item_ids,
                item_range_map,
            )
            preferred_ranges.extend(
                _extend_ranges_for_ids(
                    ambiguity.related_section_ids,
                    section_range_map,
                )
            )
            resolved_spans = [
                resolve_single_span(span, preferred_ranges=preferred_ranges)
                for span in ambiguity.source_spans
            ]
            resolved_ambiguities.append(
                ambiguity.model_copy(update={"source_spans": resolved_spans})
            )

        return ResolvedSourceObjects(
            sections=resolved_sections,
            items=resolved_items,
            timeline_events=resolved_timeline_events,
            ambiguities=resolved_ambiguities,
        )
