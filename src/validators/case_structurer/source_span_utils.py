"""Shared source-span utilities for validation and deterministic correction."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.case_structurer.source_span import SourceSpan
from src.schemas.case_structurer.structured_clinical_item import StructuredClinicalItem


SourceRange = tuple[int, int]

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_ASCII_WORD_RE = re.compile(r"[A-Za-z]+")
_ALNUM_TOKEN_RE = re.compile(
    r"[A-Za-z0-9]+(?:[-_/+.][A-Za-z0-9]+)*|\d+(?:\.\d+)?%?"
)
_GENERIC_ITEM_VALUES = {
    "absent",
    "denied",
    "false",
    "none",
    "not mentioned",
    "null",
    "present",
    "true",
    "unknown",
    "yes",
    "no",
}
_SOURCE_GROUNDED_ITEM_FIELDS = {
    "body_site",
    "label",
    "time_text",
    "unit",
    "value",
}


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
    objects.extend(
        StructuredSourceObject(
            object_type="TimelineEvent",
            object_id=event.event_id,
            source_spans=event.source_spans,
        )
        for event in result.timeline_events
    )
    objects.extend(
        StructuredSourceObject(
            object_type="AmbiguityItem",
            object_id=ambiguity.ambiguity_id,
            source_spans=ambiguity.source_spans,
        )
        for ambiguity in result.ambiguities
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


def item_field_values(item: StructuredClinicalItem) -> dict[str, str | None]:
    return {
        "label": item.label,
        "value": item.value,
        "unit": item.unit,
        "body_site": item.body_site,
        "time_text": item.time_text,
    }


def unsupported_item_fields(
    item: StructuredClinicalItem,
    source_text: str,
) -> list[str]:
    unsupported_fields: list[str] = []

    for field_name, value in item_field_values(item).items():
        if not should_validate_item_field(field_name, value, source_text):
            continue

        if not item_field_supported_by_source(
            field_name=field_name,
            value=value or "",
            source_text=source_text,
        ):
            unsupported_fields.append(field_name)

    return unsupported_fields


def should_validate_item_field(
    field_name: str,
    value: str | None,
    source_text: str,
) -> bool:
    if value is None:
        return False

    cleaned = value.strip()
    if not cleaned:
        return False

    if field_name == "value" and cleaned.lower() in _GENERIC_ITEM_VALUES:
        return False

    if field_name in _SOURCE_GROUNDED_ITEM_FIELDS:
        return True

    if has_cjk(cleaned):
        return True

    if has_non_alpha_source_token(cleaned):
        return True

    return not has_cjk(source_text)


def item_field_supported_by_source(
    field_name: str,
    value: str,
    source_text: str,
) -> bool:
    cleaned = value.strip()
    if not cleaned:
        return True

    if normalized_contains(source_text, cleaned):
        return True

    if field_name in {"time_text", "unit"}:
        return False

    return source_like_text_covered_by_source(cleaned, source_text)


def source_like_text_covered_by_source(value: str, source_text: str) -> bool:
    required_tokens = required_alnum_tokens(value)
    normalized_source = normalize_text_for_match(source_text).lower()
    if any(token.lower() not in normalized_source for token in required_tokens):
        return False

    chunks = cjk_chunks(value)
    if not chunks:
        return bool(required_tokens)

    return all(cjk_chunk_covered_by_source(chunk, source_text) for chunk in chunks)


def cjk_chunk_covered_by_source(chunk: str, source_text: str) -> bool:
    if len(chunk) == 1:
        return chunk in source_text

    normalized_chunk = normalize_text_for_match(chunk)
    if normalized_chunk in source_text:
        return True

    covered = [False] * len(normalized_chunk)
    for start in range(len(normalized_chunk)):
        for end in range(len(normalized_chunk), start + 1, -1):
            candidate = normalized_chunk[start:end]
            if len(candidate) < 2:
                continue
            if candidate in source_text:
                for index in range(start, end):
                    covered[index] = True
                break

    return sum(covered) / len(normalized_chunk) >= 0.75


def normalized_contains(text: str, query: str) -> bool:
    return normalize_text_for_match(query).lower() in normalize_text_for_match(
        text
    ).lower()


def has_cjk(text: str) -> bool:
    return _CJK_RE.search(text) is not None


def has_non_alpha_source_token(text: str) -> bool:
    return any(
        char.isdigit() or (not char.isalpha() and not char.isspace())
        for char in text
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
        if has_cjk(char):
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
