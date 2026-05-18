"""Shared source-span utilities for validation and deterministic correction."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.source_span import SourceSpan


SourceRange = tuple[int, int]

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_ASCII_WORD_RE = re.compile(r"[A-Za-z]+")
_ALNUM_TOKEN_RE = re.compile(
    r"[A-Za-z0-9]+(?:[-_/+.][A-Za-z0-9]+)*|\d+(?:\.\d+)?%?"
)
_SPAN_UNIT_RE = re.compile(r"[^。；;，,\n]+[。；;，,]?\s*")


@dataclass(frozen=True)
class StructuredSourceObject:
    """A source-span-bearing object from CaseStructuringResult."""

    object_type: str
    object_id: str
    source_spans: Sequence[SourceSpan]
    parent_section_id: str | None = None


def normalize_text_for_match(text: str) -> str:
    """Collapse all whitespace runs to single spaces for fallback matching."""
    return " ".join(text.split())


def offsets_in_bounds(raw_text: str, char_start: int, char_end: int) -> bool:
    return 0 <= char_start < char_end <= len(raw_text)


def span_slice_matches(
    raw_text: str,
    quoted_text: str,
    char_start: int,
    char_end: int,
) -> bool:
    """Return whether the resolved raw_text slice matches quoted_text."""
    if not offsets_in_bounds(raw_text, char_start, char_end):
        return False

    raw_slice = raw_text[char_start:char_end]
    if raw_slice == quoted_text:
        return True

    return normalize_text_for_match(raw_slice) == normalize_text_for_match(
        quoted_text
    )


def quoted_text_exists(raw_text: str, quoted_text: str) -> bool:
    """Return whether quoted_text can be found in raw_text."""
    if not quoted_text:
        return False

    if quoted_text in raw_text:
        return True

    normalized_quote = normalize_text_for_match(quoted_text)
    if not normalized_quote:
        return False

    return normalized_quote in normalize_text_for_match(raw_text)


def get_all_structured_objects(
    result: CaseStructuringResult,
) -> list[StructuredSourceObject]:
    """Return all source-span-bearing objects in a CaseStructuringResult."""
    objects: list[StructuredSourceObject] = []

    objects.extend(
        StructuredSourceObject(
            object_type="ClinicalSection",
            object_id=section.section_id,
            source_spans=section.source_spans,
        )
        for section in result.clinical_sections
    )
    objects.extend(
        StructuredSourceObject(
            object_type="StructuredClinicalItem",
            object_id=item.item_id,
            source_spans=item.source_spans,
            parent_section_id=item.section_id,
        )
        for item in result.structured_items
    )
    return objects


def resolved_range(span: SourceSpan, raw_text: str) -> SourceRange | None:
    if span.char_start is None or span.char_end is None:
        return None

    if not offsets_in_bounds(raw_text, span.char_start, span.char_end):
        return None

    return (span.char_start, span.char_end)


def section_range_map(
    result: CaseStructuringResult,
    raw_text: str,
) -> dict[str, list[SourceRange]]:
    ranges: dict[str, list[SourceRange]] = {}

    for section in result.clinical_sections:
        for span in section.source_spans:
            span_range = resolved_range(span, raw_text)
            if span_range is not None:
                ranges.setdefault(section.section_id, []).append(span_range)

    return ranges


def range_inside_any_parent(
    item_range: SourceRange,
    parent_ranges: Sequence[SourceRange],
) -> bool:
    item_start, item_end = item_range

    return any(
        parent_start <= item_start and item_end <= parent_end
        for parent_start, parent_end in parent_ranges
    )


def combined_existing_span_text(
    raw_text: str,
    source_spans: Sequence[SourceSpan],
) -> str:
    return " ".join(
        span.quoted_text
        for span in source_spans
        if quoted_text_exists(raw_text, span.quoted_text)
    )


def required_alnum_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in _ALNUM_TOKEN_RE.findall(text):
        if _ASCII_WORD_RE.fullmatch(token) and len(token) < 2:
            continue
        tokens.append(token)

    return tokens


def cjk_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current_chars: list[str] = []

    for char in text:
        if _CJK_RE.search(char) is not None:
            current_chars.append(char)
        elif current_chars:
            chunks.append("".join(current_chars))
            current_chars = []

    if current_chars:
        chunks.append("".join(current_chars))

    return chunks


def find_all_occurrences(
    text: str,
    query: str,
    ranges: Sequence[SourceRange] | None = None,
) -> list[SourceRange]:
    """Return all exact query occurrences, optionally constrained by ranges."""
    if not query:
        return []

    search_ranges = list(ranges or [(0, len(text))])
    occurrences: list[SourceRange] = []

    for range_start, range_end in valid_ranges(text, search_ranges):
        cursor = range_start
        while True:
            start = text.find(query, cursor, range_end)
            if start < 0:
                break

            end = start + len(query)
            occurrences.append((start, end))
            cursor = start + 1

    return occurrences


def find_resolvable_span_pieces(
    raw_text: str,
    quoted_text: str,
    ranges: Sequence[SourceRange] | None = None,
    min_piece_length: int = 6,
) -> list[SourceRange]:
    """Find long exact pieces of a synthetic quote inside raw_text.

    This is intentionally conservative. It only returns exact raw_text ranges
    for pieces that can be located, and it never invents paraphrased text.
    """
    if quoted_text in raw_text:
        return []

    units = [
        match.group(0).strip()
        for match in _SPAN_UNIT_RE.finditer(quoted_text)
        if match.group(0).strip()
    ]
    if not units:
        return []

    found_ranges: list[SourceRange] = []
    index = 0
    while index < len(units):
        best_range: SourceRange | None = None
        best_end_index: int | None = None

        for end_index in range(len(units), index, -1):
            candidate = "".join(units[index:end_index]).strip()
            if len(candidate) < min_piece_length:
                continue

            occurrences = find_all_occurrences(raw_text, candidate, ranges)
            if not occurrences:
                occurrences = find_all_occurrences(raw_text, candidate)
            if not occurrences:
                continue

            if ranges:
                best_range = choose_nearest_occurrence(occurrences, ranges)
            else:
                best_range = occurrences[0]
            best_end_index = end_index
            break

        if best_range is None or best_end_index is None:
            index += 1
            continue

        found_ranges.append(best_range)
        index = best_end_index

    return merge_source_ranges(found_ranges)


def merge_source_ranges(ranges: Sequence[SourceRange]) -> list[SourceRange]:
    """Merge overlapping or touching source ranges."""
    if not ranges:
        return []

    ordered = sorted(ranges)
    merged: list[SourceRange] = [ordered[0]]
    for start, end in ordered[1:]:
        previous_start, previous_end = merged[-1]
        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
            continue
        merged.append((start, end))
    return merged


def valid_ranges(text: str, ranges: Sequence[SourceRange]) -> list[SourceRange]:
    text_length = len(text)
    bounded_ranges: list[SourceRange] = []
    for start, end in ranges:
        bounded_start = max(0, start)
        bounded_end = min(text_length, end)
        if bounded_start < bounded_end:
            bounded_ranges.append((bounded_start, bounded_end))

    return bounded_ranges


def choose_nearest_occurrence(
    occurrences: Sequence[SourceRange],
    preferred_ranges: Sequence[SourceRange],
) -> SourceRange | None:
    """Choose the exact occurrence closest to any preferred context range."""
    if not occurrences or not preferred_ranges:
        return None

    usable_ranges = [(start, end) for start, end in preferred_ranges if start <= end]
    if not usable_ranges:
        return None

    return min(
        occurrences,
        key=lambda occurrence: (
            min(range_distance(occurrence, preferred) for preferred in usable_ranges),
            occurrence[0],
            occurrence[1],
        ),
    )


def range_distance(left: SourceRange, right: SourceRange) -> int:
    left_start, left_end = left
    right_start, right_end = right

    if left_end < right_start:
        return right_start - left_end
    if right_end < left_start:
        return left_start - right_end
    return 0
