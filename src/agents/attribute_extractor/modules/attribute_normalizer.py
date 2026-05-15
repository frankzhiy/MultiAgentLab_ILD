from __future__ import annotations

import re

from src.schemas.attribute_extractor.attribute_role import AttributeRole

from .attribute_span_validator import AttributeDraftPayload

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")


class AttributeNormalizer:
    """Apply lightweight deterministic normalization to validated attributes."""

    def normalize(self, payload: AttributeDraftPayload) -> AttributeDraftPayload:
        normalized_payloads: list[dict] = []
        for attribute in payload.attribute_payloads:
            normalized = dict(attribute)
            role = AttributeRole(normalized["attribute_role"])
            span_text = str(normalized["span_text"])

            if role == AttributeRole.AGE:
                _normalize_number_with_unit(normalized, span_text, "岁", "year")
            elif role in {
                AttributeRole.SYMPTOM_DURATION,
                AttributeRole.DISEASE_HISTORY_DURATION,
                AttributeRole.WORSENING_INTERVAL,
            }:
                _normalize_duration(normalized, span_text)
            elif role == AttributeRole.SEX:
                _normalize_sex(normalized, span_text)
            elif role == AttributeRole.QUALITATIVE_RESULT:
                _normalize_qualitative(normalized, span_text)
            elif role == AttributeRole.ABNORMAL_DIRECTION:
                _normalize_direction(normalized, span_text)

            normalized_payloads.append(normalized)

        return AttributeDraftPayload(
            attribute_payloads=normalized_payloads,
            warnings=payload.warnings,
        )


def _normalize_number_with_unit(
    attribute: dict,
    span_text: str,
    source_unit: str,
    normalized_unit: str,
) -> None:
    if source_unit not in span_text:
        return
    value = _first_number(span_text)
    if value is None:
        return
    attribute["normalized_value"] = value
    attribute["normalized_unit"] = normalized_unit


def _normalize_duration(attribute: dict, span_text: str) -> None:
    unit_map = {
        "年": "year",
        "月": "month",
        "天": "day",
        "日": "day",
        "周": "week",
    }
    value = _first_number(span_text)
    if value is None:
        return
    for source_unit, normalized_unit in unit_map.items():
        if source_unit in span_text:
            attribute["normalized_value"] = value
            attribute["normalized_unit"] = normalized_unit
            return


def _normalize_sex(attribute: dict, span_text: str) -> None:
    if span_text == "女":
        attribute["normalized_text"] = "female"
    elif span_text == "男":
        attribute["normalized_text"] = "male"


def _normalize_qualitative(attribute: dict, span_text: str) -> None:
    if "阳性" in span_text:
        attribute["normalized_text"] = "positive"
    elif "阴性" in span_text:
        attribute["normalized_text"] = "negative"
    elif "正常" in span_text:
        attribute["normalized_text"] = "normal"


def _normalize_direction(attribute: dict, span_text: str) -> None:
    if any(term in span_text for term in ("增高", "升高")):
        attribute["normalized_text"] = "increased"
    elif any(term in span_text for term in ("降低", "减低")):
        attribute["normalized_text"] = "decreased"
    elif "正常" in span_text:
        attribute["normalized_text"] = "normal"


def _first_number(text: str) -> int | float | None:
    match = _NUMBER_PATTERN.search(text)
    if match is None:
        return None
    raw_value = match.group(0)
    if "." in raw_value:
        return float(raw_value)
    return int(raw_value)
