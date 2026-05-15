from __future__ import annotations

import re
from dataclasses import dataclass

from .atomization_candidate_builder import AtomizationCandidate
from .coverage_units import CoverageUnit, CoverageUnitBuildResult


SYMPTOM_TERMS = (
    "呼吸困难",
    "咳嗽",
    "咳痰",
    "胸闷",
    "气短",
    "发热",
    "寒战",
    "胸痛",
    "咯血",
    "乏力",
    "盗汗",
    "恶心",
    "呕吐",
)

PULMONARY_METRIC_TERMS = (
    "FEV1/FVC",
    "R5-R20",
    "DLCO",
    "FEV1",
    "FVC",
    "TLC",
    "MVV",
    "Fres",
    "Zrs",
    "R35",
    "R20",
    "R5",
    "Rc",
    "Rp",
    "X5",
    "AX",
    "Ers",
    "RV",
)

DIRECTION_TERMS = (
    "增高",
    "升高",
    "增大",
    "降低",
    "减低",
    "减损",
    "正常",
    "异常",
    "障碍",
    "阳性",
    "阴性",
)

SEPARATORS = (
    "、",
    "，",
    ",",
    ";",
    "；",
    "及",
    "和",
    "伴",
    "并",
    "且",
)

NEGATION_CUES = (
    "未见",
    "未诉",
    "否认",
    "不伴",
    "无",
    "未",
)

ANALYTE_VALUE_PATTERN = re.compile(
    r"(?P<analyte>[A-Za-z][A-Za-z0-9/+\-.()]{0,24}|"
    r"[\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9/+\-.()]{1,24})"
    r"\s*[:：]?\s*"
    r"(?:(?P<numeric_value>[<>≤≥]?\s*(?:\d+(?:\.\d+)?|\d+:\d+))"
    r"\s*(?P<unit_text>[A-Za-z%μµ/.\-^0-9×*]+|[\u4e00-\u9fff/%]+)?|"
    r"(?P<qualitative_value>[+-]|阳性|阴性|正常|异常|增高|升高|降低|减低))"
)

_SEPARATOR_PATTERN = re.compile("|".join(re.escape(separator) for separator in SEPARATORS))
_METRIC_PATTERN = re.compile(
    r"(?<![A-Za-z0-9/\-])("
    + "|".join(re.escape(term) for term in PULMONARY_METRIC_TERMS)
    + r")(?![A-Za-z0-9/\-])"
)


@dataclass(frozen=True)
class _TermMatch:
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class _AnalyteValuePair:
    analyte: str
    result_text: str
    unit_text: str | None
    start: int
    end: int


class CoverageUnitBuilder:
    """Build deterministic internal coverage units from atomization candidates."""

    def build(
        self,
        candidates: list[AtomizationCandidate],
    ) -> CoverageUnitBuildResult:
        coverage_units: list[CoverageUnit] = []
        warnings: list[str] = []

        for candidate in candidates:
            item_units = self._build_candidate_units(candidate)
            if any(unit.split_basis == "llm_required" for unit in item_units):
                warnings.append(
                    f"{candidate.item_id}: compound item requires LLM atom boundary."
                )
            coverage_units.extend(item_units)

        return CoverageUnitBuildResult(
            coverage_units=coverage_units,
            warnings=warnings,
        )

    def _build_candidate_units(
        self,
        candidate: AtomizationCandidate,
    ) -> list[CoverageUnit]:
        text = _candidate_text(candidate)
        analyte_pairs = _find_analyte_value_pairs(text, candidate)
        metrics = _find_metric_terms(text)
        symptoms = _find_literal_terms(text, SYMPTOM_TERMS)
        direction = _first_direction(candidate, text)
        is_negated = _is_negated_candidate(candidate, text)

        if candidate.item_type == "lab_result" and len(analyte_pairs) > 1:
            return [
                self._unit(
                    candidate=candidate,
                    index=index,
                    surface_text=_format_result_phrase(
                        pair.analyte,
                        pair.result_text,
                        pair.unit_text,
                    ),
                    clinical_object=pair.analyte,
                    result_text=pair.result_text,
                    unit_text=pair.unit_text,
                    split_basis="analyte_value_pair",
                )
                for index, pair in enumerate(analyte_pairs, start=1)
            ]

        if len(metrics) > 1 and direction is not None:
            return [
                self._unit(
                    candidate=candidate,
                    index=index,
                    surface_text=_format_status_phrase(metric.text, direction),
                    clinical_object=metric.text,
                    status_or_direction=direction,
                    split_basis="shared_direction_metrics",
                )
                for index, metric in enumerate(metrics, start=1)
            ]

        if is_negated and len(symptoms) > 1:
            return [
                self._unit(
                    candidate=candidate,
                    index=index,
                    surface_text=f"无{symptom.text}",
                    clinical_object=symptom.text,
                    assertion_status="absent",
                    split_basis="negated_finding",
                )
                for index, symptom in enumerate(symptoms, start=1)
            ]

        if len(symptoms) > 1:
            return [
                self._unit(
                    candidate=candidate,
                    index=index,
                    surface_text=_format_status_phrase(symptom.text, direction),
                    clinical_object=symptom.text,
                    status_or_direction=direction,
                    assertion_status=_assertion_status_for_object(
                        candidate,
                        text,
                        symptom,
                    ),
                    split_basis="shared_modifier_clinical_objects",
                )
                for index, symptom in enumerate(symptoms, start=1)
            ]

        if candidate.item_type == "lab_result" and len(analyte_pairs) == 1:
            pair = analyte_pairs[0]
            return [
                self._unit(
                    candidate=candidate,
                    index=1,
                    surface_text=_format_result_phrase(
                        pair.analyte,
                        pair.result_text,
                        pair.unit_text,
                    ),
                    clinical_object=pair.analyte,
                    result_text=pair.result_text,
                    unit_text=pair.unit_text,
                    split_basis="atomic_candidate",
                )
            ]

        if len(metrics) == 1:
            metric = metrics[0]
            return [
                self._unit(
                    candidate=candidate,
                    index=1,
                    surface_text=_format_status_phrase(metric.text, direction),
                    clinical_object=metric.text,
                    status_or_direction=direction,
                    split_basis="atomic_candidate",
                )
            ]

        if len(symptoms) == 1:
            symptom = symptoms[0]
            return [
                self._unit(
                    candidate=candidate,
                    index=1,
                    surface_text=_format_status_phrase(symptom.text, direction),
                    clinical_object=symptom.text,
                    status_or_direction=direction,
                    assertion_status=_assertion_status_for_object(
                        candidate,
                        text,
                        symptom,
                    ),
                    split_basis="atomic_candidate",
                )
            ]

        if is_negated and _looks_compound(text):
            findings = _split_candidate_label(candidate)
            if len(findings) > 1:
                return [
                    self._unit(
                        candidate=candidate,
                        index=index,
                        surface_text=f"无{finding}",
                        clinical_object=finding,
                        assertion_status="absent",
                        split_basis="negated_finding",
                    )
                    for index, finding in enumerate(findings, start=1)
                ]

        split_basis = "llm_required" if _looks_compound(text) else "atomic_candidate"
        return [
            self._unit(
                candidate=candidate,
                index=1,
                surface_text=_atomic_surface_text(candidate),
                clinical_object=_clinical_object_default(candidate),
                status_or_direction=direction,
                split_basis=split_basis,
            )
        ]

    def _unit(
        self,
        *,
        candidate: AtomizationCandidate,
        index: int,
        surface_text: str,
        clinical_object: str,
        split_basis: str,
        status_or_direction: str | None = None,
        result_text: str | None = None,
        unit_text: str | None = None,
        assertion_status: str | None = None,
    ) -> CoverageUnit:
        return CoverageUnit(
            unit_id=f"{candidate.item_id}__unit_{index:03d}",
            source_item_id=candidate.item_id,
            source_attribute_ids=_attribute_ids(candidate),
            source_span_ids=_span_ids(candidate),
            surface_text=_compact_text(surface_text),
            clinical_object=_compact_text(clinical_object),
            status_or_direction=_optional_text(status_or_direction),
            modifier_texts=_modifier_texts(
                candidate=candidate,
                status_or_direction=status_or_direction,
                result_text=result_text,
                unit_text=unit_text,
            ),
            assertion_status=assertion_status or candidate.negation,
            certainty=candidate.certainty,
            temporality=candidate.temporality,
            split_basis=split_basis,
            required=True,
        )


def _candidate_text(candidate: AtomizationCandidate) -> str:
    if candidate.source_text.strip():
        return candidate.source_text.strip()

    parts = [
        candidate.label,
        candidate.source_text,
    ]
    return " ".join(part.strip() for part in parts if part and part.strip())


def _span_ids(candidate: AtomizationCandidate) -> list[str]:
    span_ids: list[str] = []
    for span in candidate.source_spans:
        span_id = span.get("span_id")
        if not isinstance(span_id, str):
            continue
        cleaned = span_id.strip()
        if cleaned and cleaned not in span_ids:
            span_ids.append(cleaned)
    return span_ids


def _find_literal_terms(text: str, terms: tuple[str, ...]) -> list[_TermMatch]:
    matches: list[_TermMatch] = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text):
            matches.append(_TermMatch(term, match.start(), match.end()))
    return _dedupe_matches(matches)


def _find_metric_terms(text: str) -> list[_TermMatch]:
    matches = [
        _TermMatch(match.group(1), match.start(1), match.end(1))
        for match in _METRIC_PATTERN.finditer(text)
    ]
    return _dedupe_matches(matches)


def _find_analyte_value_pairs(
    text: str,
    candidate: AtomizationCandidate,
) -> list[_AnalyteValuePair]:
    if candidate.item_type != "lab_result":
        return []

    pairs: list[_AnalyteValuePair] = []
    for match in ANALYTE_VALUE_PATTERN.finditer(text):
        analyte = _optional_text(match.group("analyte"))
        result_text = _optional_text(
            match.group("numeric_value") or match.group("qualitative_value")
        )
        if analyte is None or result_text is None:
            continue
        pairs.append(
            _AnalyteValuePair(
                analyte=analyte,
                result_text=result_text,
                unit_text=_optional_text(match.group("unit_text")),
                start=match.start(),
                end=match.end(),
            )
        )
    return _dedupe_analyte_pairs(pairs)


def _dedupe_matches(matches: list[_TermMatch]) -> list[_TermMatch]:
    matches = sorted(matches, key=lambda item: (item.start, -(item.end - item.start)))
    result: list[_TermMatch] = []
    occupied: list[range] = []
    seen_text: set[str] = set()

    for match in matches:
        if match.text in seen_text:
            continue
        if any(match.start < span.stop and match.end > span.start for span in occupied):
            continue
        result.append(match)
        occupied.append(range(match.start, match.end))
        seen_text.add(match.text)

    return sorted(result, key=lambda item: item.start)


def _dedupe_analyte_pairs(
    pairs: list[_AnalyteValuePair],
) -> list[_AnalyteValuePair]:
    result: list[_AnalyteValuePair] = []
    seen: set[tuple[str, str, str | None]] = set()
    for pair in sorted(pairs, key=lambda item: item.start):
        key = (pair.analyte, pair.result_text, pair.unit_text)
        if key in seen:
            continue
        seen.add(key)
        result.append(pair)
    return result


def _first_direction(
    candidate: AtomizationCandidate,
    text: str,
) -> str | None:
    for attribute in candidate.attributes:
        if attribute.attribute_role not in {"abnormal_direction", "qualitative_result"}:
            continue
        if attribute.span_text in DIRECTION_TERMS:
            return attribute.span_text
        if isinstance(attribute.normalized_text, str):
            if attribute.normalized_text == "increased":
                return "增高"
            if attribute.normalized_text == "decreased":
                return "降低"
            if attribute.normalized_text == "normal":
                return "正常"
    for term in DIRECTION_TERMS:
        if term in text:
            return term
    return None


def _is_negated_candidate(
    candidate: AtomizationCandidate,
    text: str,
) -> bool:
    if candidate.negation in {"absent", "denied"}:
        return True
    return any(cue in text for cue in NEGATION_CUES)


def _assertion_status_for_object(
    candidate: AtomizationCandidate,
    text: str,
    term: _TermMatch,
) -> str:
    prefix = text[max(0, term.start - 8) : term.start]
    if candidate.negation in {"absent", "denied"} or any(
        cue in prefix for cue in NEGATION_CUES
    ):
        return "absent"
    return candidate.negation


def _looks_compound(text: str) -> bool:
    return bool(_SEPARATOR_PATTERN.search(text))


def _split_candidate_label(candidate: AtomizationCandidate) -> list[str]:
    parts = [
        _optional_text(part)
        for part in _SEPARATOR_PATTERN.split(candidate.label)
    ]
    return [part for part in parts if part is not None]


def _format_result_phrase(
    clinical_object: str,
    result_text: str | None,
    unit_text: str | None,
) -> str:
    if result_text is None:
        return clinical_object
    if unit_text is None:
        return f"{clinical_object} {result_text}"
    return f"{clinical_object} {result_text} {unit_text}"


def _format_status_phrase(
    clinical_object: str,
    status_or_direction: str | None,
) -> str:
    if status_or_direction is None:
        return clinical_object
    return f"{clinical_object}{status_or_direction}"


def _atomic_surface_text(candidate: AtomizationCandidate) -> str:
    return candidate.label


def _clinical_object_default(candidate: AtomizationCandidate) -> str:
    return candidate.label


def _compact_text(text: str, limit: int = 160) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return f"{compacted[: limit - 3]}..."


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _attribute_ids(candidate: AtomizationCandidate) -> list[str]:
    return [attribute.attribute_id for attribute in candidate.attributes]


def _modifier_texts(
    *,
    candidate: AtomizationCandidate,
    status_or_direction: str | None,
    result_text: str | None,
    unit_text: str | None,
) -> list[str]:
    texts: list[str] = []
    for attribute in candidate.attributes:
        if attribute.span_text not in texts:
            texts.append(attribute.span_text)
    for candidate_text in (status_or_direction, result_text, unit_text):
        cleaned = _optional_text(candidate_text)
        if cleaned is not None and cleaned not in texts:
            texts.append(cleaned)
    return texts
