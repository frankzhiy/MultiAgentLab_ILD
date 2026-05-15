from __future__ import annotations

from typing import Any

from src.agents.evidence_atomizer.prompting.output_skeletons import (
    clinical_assertion_output_skeleton,
)
from src.agents.evidence_atomizer.prompting.prompt_context import (
    format_atomization_boundary,
    format_atomization_candidates,
    format_forbidden_downstream_objects,
)
from src.agents.evidence_atomizer.prompting.schema_contracts import (
    clinical_assertion_labeling_contract,
)
from src.schemas.case_structurer.common import ConfidenceLevel, NegationStatus
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
    ClinicalObjectAssertion,
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)

from .atomization_candidate_builder import AtomizationCandidate
from .base_llm_extractor import BaseLLMExtractor
from .clinical_assertion_validator import ClinicalAssertionValidator


class ClinicalAssertionResolver(BaseLLMExtractor):
    """Resolve object-level clinical assertions for atomization candidates."""

    _LLM_ITEM_TYPES = frozenset(
        {
            "symptom",
            "sign",
            "treatment_response",
            "diagnosis_history",
            "follow_up_finding",
            "imaging_finding",
        }
    )
    _COORDINATED_SYMPTOM_TERMS = (
        "午后低热",
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.validator = ClinicalAssertionValidator()

    def resolve(
        self,
        candidates: list[AtomizationCandidate],
    ) -> ClinicalAssertionResolutionResult:
        assertions: list[ClinicalObjectAssertion] = []
        warnings = []

        for candidate in candidates:
            source_text = candidate.source_text.strip()
            if not source_text:
                continue

            if self._should_use_llm(candidate):
                payload = self._resolve_candidate_payload(candidate)
                result = self.validator.validate(candidate, payload)
            else:
                result = ClinicalAssertionResolutionResult()

            result = self._refine_resolution(candidate, result)

            assertions.extend(result.clinical_object_assertions)
            warnings.extend(result.assertion_warnings)

        return ClinicalAssertionResolutionResult(
            clinical_object_assertions=assertions,
            assertion_warnings=warnings,
        )

    def _resolve_candidate_payload(
        self,
        candidate: AtomizationCandidate,
    ) -> dict[str, Any]:
        template_vars = {
            **clinical_assertion_labeling_contract(),
            "atomization_boundary": format_atomization_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "atomization_candidate": format_atomization_candidates([candidate]),
            "output_skeleton": clinical_assertion_output_skeleton(),
        }
        content = self.generate_json(
            prompt_path=self.prompt_path("clinical_assertion_labeling"),
            user_payload={
                "atomization_candidate": candidate.model_dump(mode="json"),
            },
            instruction=(
                "Return exactly one JSON object with keys "
                "clinical_object_assertions and assertion_warnings."
            ),
            template_vars=template_vars,
            response_format="json_object",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("Clinical assertion resolver payload must be a JSON object.")
        return payload

    def _should_use_llm(self, candidate: AtomizationCandidate) -> bool:
        return candidate.item_type in self._LLM_ITEM_TYPES

    def _refine_resolution(
        self,
        candidate: AtomizationCandidate,
        result: ClinicalAssertionResolutionResult,
    ) -> ClinicalAssertionResolutionResult:
        refined_assertions: list[ClinicalObjectAssertion] = []

        for assertion in result.clinical_object_assertions:
            split_terms = self._split_coordinated_symptom_terms(assertion)
            if len(split_terms) <= 1:
                refined_assertions.append(assertion)
                continue

            for term in split_terms:
                refined_assertions.append(
                    ClinicalObjectAssertion(
                        source_item_id=assertion.source_item_id,
                        object_text=term,
                        object_type=assertion.object_type,
                        assertion_status=assertion.assertion_status,
                        assertion_cue_text=assertion.assertion_cue_text,
                        assertion_scope_text=assertion.assertion_scope_text,
                        context_text=assertion.context_text,
                        source_span_ids=assertion.source_span_ids,
                        confidence=assertion.confidence,
                        notes=assertion.notes,
                    )
                )

        if not any(
            assertion.object_type == ClinicalObjectType.CARE_SEEKING_OR_MANAGEMENT
            for assertion in refined_assertions
        ):
            synthesized = self._synthesize_care_seeking_assertion(candidate)
            if synthesized is not None:
                refined_assertions.append(synthesized)

        return ClinicalAssertionResolutionResult(
            clinical_object_assertions=_dedupe_assertions(refined_assertions),
            assertion_warnings=result.assertion_warnings,
        )

    def _split_coordinated_symptom_terms(
        self,
        assertion: ClinicalObjectAssertion,
    ) -> list[str]:
        if assertion.object_type != ClinicalObjectType.SYMPTOM:
            return [assertion.object_text]

        object_text = assertion.object_text
        matches: list[str] = []
        for term in self._COORDINATED_SYMPTOM_TERMS:
            if term not in object_text:
                continue
            if term not in matches:
                matches.append(term)

        if len(matches) <= 1:
            return [object_text]
        return matches

    def _synthesize_care_seeking_assertion(
        self,
        candidate: AtomizationCandidate,
    ) -> ClinicalObjectAssertion | None:
        source_text = candidate.source_text.strip()
        scope_text = None
        for candidate_scope in (
            "未予重视及诊疗",
            "未予诊疗",
            "未予重视及治疗",
        ):
            if candidate_scope in source_text:
                scope_text = candidate_scope
                break

        if scope_text is None:
            return None

        object_text = None
        for candidate_object in ("重视及诊疗", "诊疗", "重视及治疗", "治疗"):
            if candidate_object in scope_text or candidate_object in source_text:
                object_text = candidate_object
                break

        if object_text is None:
            return None

        return ClinicalObjectAssertion(
            source_item_id=candidate.item_id,
            object_text=object_text,
            object_type=ClinicalObjectType.CARE_SEEKING_OR_MANAGEMENT,
            assertion_status=ClinicalObjectAssertionStatus.ABSENT,
            assertion_cue_text="未予" if "未予" in scope_text else "未",
            assertion_scope_text=scope_text,
            context_text=source_text,
            source_span_ids=_span_ids(candidate),
            confidence=ConfidenceLevel.MEDIUM,
            notes=None,
        )


def _dedupe_assertions(
    assertions: list[ClinicalObjectAssertion],
) -> list[ClinicalObjectAssertion]:
    deduped: list[ClinicalObjectAssertion] = []
    seen_keys: set[tuple[str, str, str, str | None]] = set()

    for assertion in assertions:
        key = (
            assertion.object_text,
            assertion.object_type.value,
            assertion.assertion_status.value,
            assertion.assertion_scope_text,
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(assertion)

    return deduped


def _span_ids(candidate: AtomizationCandidate) -> list[str]:
    span_ids: list[str] = []
    for span in candidate.source_spans:
        span_id = span.get("span_id")
        if isinstance(span_id, str) and span_id.strip() and span_id not in span_ids:
            span_ids.append(span_id)
    return span_ids