from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.agents.evidence_atomizer.prompting.prompt_context import (
    format_atomization_boundary,
    format_atomization_candidates,
    format_forbidden_downstream_objects,
)
from src.schemas.evidence_atomizer import AtomizationWarning
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalObjectAssertion,
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_atomizer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
    ValidationSeverity,
)
from src.schemas.evidence_atomizer.evidence_event_frame import (
    AtomizationPolicy,
    ContextRole,
    EvidenceEventFrame,
    EvidenceEventFrameBuildResult,
    EvidenceFrameNode,
    FrameNodeType,
)
from src.utils.id_generator import generate_evidence_frame_id

from .atomization_candidate_builder import AtomizationCandidate
from .base_llm_extractor import BaseLLMExtractor
from .evidence_event_frame_validator import EvidenceEventFrameValidator


class EvidenceEventFrameBuilder(BaseLLMExtractor):
    """Build tree-like EvidenceEventFrame objects for atomization candidates."""

    _MAX_BUILD_ATTEMPTS = 2

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.validator = EvidenceEventFrameValidator()

    def build(
        self,
        *,
        candidates: list[AtomizationCandidate],
        assertions: list[ClinicalObjectAssertion],
    ) -> EvidenceEventFrameBuildResult:
        assertions_by_item_id: dict[str, list[ClinicalObjectAssertion]] = defaultdict(list)
        for assertion in assertions:
            assertions_by_item_id[assertion.source_item_id].append(assertion)

        frames: list[EvidenceEventFrame] = []
        warnings: list[AtomizationWarning] = []

        for candidate in candidates:
            source_text = candidate.source_text.strip()
            if not source_text:
                warnings.append(
                    _warning(
                        code="frame_missing_source_text",
                        message="EvidenceEventFrame was skipped because candidate.source_text was empty.",
                        related_item_id=candidate.item_id,
                    )
                )
                continue

            candidate_assertions = assertions_by_item_id.get(candidate.item_id, [])
            repair_feedback: list[str] = []
            frame: EvidenceEventFrame | None = None

            for attempt in range(1, self._MAX_BUILD_ATTEMPTS + 1):
                draft_payload = self._build_candidate_payload(
                    candidate,
                    candidate_assertions,
                    repair_feedback if attempt > 1 else None,
                )
                frame, frame_warnings = self.validator.validate(
                    candidate=candidate,
                    assertions=candidate_assertions,
                    draft_payload=draft_payload,
                )
                warnings.extend(frame_warnings)
                if frame is not None:
                    frames.append(frame)
                    break
                repair_feedback = _repair_feedback(
                    assertions=candidate_assertions,
                    warnings=frame_warnings,
                )

            if frame is None:
                fallback_frame = _conservative_assertion_grounded_fallback_frame(
                    candidate=candidate,
                    assertions=candidate_assertions,
                )
                if fallback_frame is not None:
                    frames.append(fallback_frame)
                    warnings.extend(fallback_frame.frame_warnings)
                continue

        return EvidenceEventFrameBuildResult(frames=frames, warnings=warnings)

    def _build_candidate_payload(
        self,
        candidate: AtomizationCandidate,
        assertions: list[ClinicalObjectAssertion],
        repair_feedback: list[str] | None = None,
    ) -> dict[str, Any]:
        template_vars = {
            "atomization_boundary": format_atomization_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "atomization_candidate": format_atomization_candidates([candidate]),
            "clinical_object_assertions": _format_assertions(assertions),
            "output_skeleton": _frame_output_skeleton(candidate.item_id),
        }
        instruction_lines = [
            "Return exactly one JSON object with keys frame_nodes, deferred_assertion_ids, and frame_warnings for this single atomization candidate.",
            "Build an assertion-grounded adaptive EvidenceEventFrame.",
            "Every ClinicalObjectAssertion must be mapped through source_assertion_ids or explicitly listed in deferred_assertion_ids.",
            "Do not collapse a multi-assertion item into one atomizable full-source node.",
        ]
        if repair_feedback:
            instruction_lines.append("Repair the previous invalid frame using this validation feedback:")
            instruction_lines.extend(f"- {line}" for line in repair_feedback)
        content = self.generate_json(
            prompt_path=self.prompt_path("evidence_event_frame_building"),
            user_payload={
                "atomization_candidate": candidate.model_dump(mode="json"),
                "clinical_object_assertions": [
                    assertion.model_dump(mode="json")
                    for assertion in assertions
                ],
            },
            instruction="\n".join(instruction_lines),
            template_vars=template_vars,
            response_format="json_object",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("EvidenceEventFrame draft payload must be a JSON object.")
        if "frame_nodes" not in payload:
            payload["frame_nodes"] = []
        if "deferred_assertion_ids" not in payload:
            payload["deferred_assertion_ids"] = []
        if "frame_warnings" not in payload:
            payload["frame_warnings"] = []
        return payload


def _conservative_assertion_grounded_fallback_frame(
    *,
    candidate: AtomizationCandidate,
    assertions: list[ClinicalObjectAssertion],
) -> EvidenceEventFrame | None:
    source_text = candidate.source_text.strip()
    if not source_text:
        return None

    candidate_span_ids = _candidate_span_ids(candidate)
    candidate_attribute_ids = [attribute.attribute_id for attribute in candidate.attributes]
    frame_warnings: list[AtomizationWarning] = []

    if assertions:
        nodes: list[EvidenceFrameNode] = []
        context_node_ids: list[str] = []
        for assertion in assertions:
            node_type, context_role, atomizable, policy, warning_message = (
                _fallback_node_shape(assertion)
            )
            node = EvidenceFrameNode(
                source_item_id=candidate.item_id,
                node_type=node_type,
                node_text=assertion.object_text,
                assertion_status=_fallback_assertion_status(assertion),
                certainty=_fallback_certainty(candidate, assertion),
                temporality=_coerce_enum(
                    candidate.temporality,
                    TemporalRelation,
                    TemporalRelation.UNKNOWN,
                ),
                inherited_context_node_ids=[],
                source_assertion_ids=[assertion.object_id],
                source_attribute_ids=candidate_attribute_ids,
                source_span_ids=assertion.source_span_ids or candidate_span_ids,
                context_role=context_role,
                atomizable=atomizable,
                atomization_policy=policy,
                confidence=ConfidenceLevel.LOW,
                notes=None,
            )
            nodes.append(node)
            if node.node_type == FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT:
                context_node_ids.append(node.frame_node_id)
            if warning_message is not None:
                frame_warnings.append(
                    _warning(
                        code="frame_builder_fallback_mapping_warning",
                        message=warning_message,
                        related_item_id=candidate.item_id,
                    )
                )

        if context_node_ids:
            nodes = [
                node
                if node.node_type == FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT
                else node.model_copy(
                    update={
                        "inherited_context_node_ids": [
                            context_id
                            for context_id in context_node_ids
                            if context_id != node.frame_node_id
                        ]
                    }
                )
                for node in nodes
            ]

        frame_warnings.insert(
            0,
            _warning(
                code="frame_builder_fallback_used",
                message=(
                    "A conservative assertion-grounded EvidenceEventFrame fallback was used after draft validation failed. "
                    "Each ClinicalObjectAssertion was preserved as its own frame node or context node."
                ),
                related_item_id=candidate.item_id,
            ),
        )
        return EvidenceEventFrame(
            frame_id=generate_evidence_frame_id(),
            source_item_id=candidate.item_id,
            source_text=source_text,
            frame_nodes=nodes,
            deferred_assertion_ids=[],
            frame_warnings=frame_warnings,
        )

    if _is_complex_candidate(candidate):
        node = EvidenceFrameNode(
            source_item_id=candidate.item_id,
            node_type=FrameNodeType.UNCERTAIN_OR_OTHER,
            node_text=source_text,
            assertion_status=_coerce_enum(
                candidate.negation,
                NegationStatus,
                NegationStatus.UNKNOWN,
            ),
            certainty=_coerce_enum(
                candidate.certainty,
                CertaintyLevel,
                CertaintyLevel.UNKNOWN,
            ),
            temporality=_coerce_enum(
                candidate.temporality,
                TemporalRelation,
                TemporalRelation.UNKNOWN,
            ),
            context_role=ContextRole.UNCERTAIN,
            atomizable=False,
            atomization_policy=AtomizationPolicy.DEFER,
            confidence=ConfidenceLevel.LOW,
            source_attribute_ids=candidate_attribute_ids,
            source_span_ids=candidate_span_ids,
        )
        return EvidenceEventFrame(
            frame_id=generate_evidence_frame_id(),
            source_item_id=candidate.item_id,
            source_text=source_text,
            frame_nodes=[node],
            deferred_assertion_ids=[],
            frame_warnings=[
                _warning(
                    code="frame_builder_fallback_used",
                    message=(
                        "No ClinicalObjectAssertions were available for a complex candidate, so the fallback frame was marked non-atomizable and deferred."
                    ),
                    related_item_id=candidate.item_id,
                )
            ],
        )

    node = EvidenceFrameNode(
        source_item_id=candidate.item_id,
        node_type=FrameNodeType.UNCERTAIN_OR_OTHER,
        node_text=source_text,
        assertion_status=_coerce_enum(
            candidate.negation,
            NegationStatus,
            NegationStatus.UNKNOWN,
        ),
        certainty=_coerce_enum(
            candidate.certainty,
            CertaintyLevel,
            CertaintyLevel.UNKNOWN,
        ),
        temporality=_coerce_enum(
            candidate.temporality,
            TemporalRelation,
            TemporalRelation.UNKNOWN,
        ),
        context_role=ContextRole.LOCAL_CONTENT,
        atomizable=True,
        atomization_policy=AtomizationPolicy.GENERATE_ATOM,
        confidence=ConfidenceLevel.LOW,
        source_attribute_ids=candidate_attribute_ids,
        source_span_ids=candidate_span_ids,
    )
    return EvidenceEventFrame(
        frame_id=generate_evidence_frame_id(),
        source_item_id=candidate.item_id,
        source_text=source_text,
        frame_nodes=[node],
        deferred_assertion_ids=[],
        frame_warnings=[
            _warning(
                code="frame_builder_fallback_used",
                message=(
                    "No ClinicalObjectAssertions were available, so a simple single-node fallback frame was used for this candidate."
                ),
                related_item_id=candidate.item_id,
            )
        ],
    )


def _format_assertions(assertions: list[ClinicalObjectAssertion]) -> str:
    if not assertions:
        return "(none)"
    return "\n".join(
        "- "
        + " | ".join(
            [
                f"object_id={assertion.object_id}",
                f"source_item_id={assertion.source_item_id}",
                f"object_text={assertion.object_text}",
                f"object_type={assertion.object_type.value}",
                f"assertion_status={assertion.assertion_status.value}",
                f"assertion_cue_text={assertion.assertion_cue_text}",
                f"assertion_scope_text={assertion.assertion_scope_text}",
                f"source_span_ids={assertion.source_span_ids}",
            ]
        )
        for assertion in assertions
    )


def _frame_output_skeleton(source_item_id: str) -> str:
    return (
        "{\n"
        '  "frame_nodes": [\n'
        "    {\n"
        '      "frame_node_id": "tmp_node_001",\n'
        f'      "source_item_id": "{source_item_id}",\n'
        '      "node_type": "...",\n'
        '      "node_text": "...",\n'
        '      "assertion_status": "present",\n'
        '      "certainty": "definite",\n'
        '      "temporality": "unknown",\n'
        '      "parent_node_id": null,\n'
        '      "relation_to_parent": null,\n'
        '      "inherited_context_node_ids": [],\n'
        '      "source_assertion_ids": [],\n'
        '      "source_attribute_ids": [],\n'
        '      "source_span_ids": [],\n'
        '      "context_role": "...",\n'
        '      "atomizable": false,\n'
        '      "atomization_policy": "do_not_generate_context_only",\n'
        '      "confidence": "medium",\n'
        '      "notes": null\n'
        "    }\n"
        "  ],\n"
        '  "deferred_assertion_ids": [],\n'
        '  "frame_warnings": []\n'
        "}"
    )


def _repair_feedback(
    *,
    assertions: list[ClinicalObjectAssertion],
    warnings: list[AtomizationWarning],
) -> list[str]:
    feedback: list[str] = [
        "Rebuild an adaptive frame for this item instead of forcing a fixed template.",
        "Every ClinicalObjectAssertion must be mapped through source_assertion_ids or explicitly deferred with a warning.",
    ]
    warning_by_code = {warning.code: warning for warning in warnings}
    for code in (
        "frame_assertion_coverage_missing",
        "degenerate_frame_single_node",
        "degenerate_frame_full_source_atomizable",
        "degenerate_frame_assertions_collapsed",
        "root_whole_source_atomization_for_complex_item",
    ):
        warning = warning_by_code.get(code)
        if warning is not None:
            feedback.append(warning.message)
    if len(assertions) > 1:
        feedback.append(
            "Do not return one atomizable node whose node_text equals the full source_text when the item contains multiple assertions."
        )
    return feedback[:6]


def _candidate_span_ids(candidate: AtomizationCandidate) -> list[str]:
    return [
        span_id
        for span in candidate.source_spans
        if isinstance((span_id := span.get("span_id")), str) and span_id.strip()
    ]


def _is_complex_candidate(candidate: AtomizationCandidate) -> bool:
    source_text = candidate.source_text.strip()
    delimiters = ("，", ",", "；", ";", "\n", "、", " and ", "伴", "并", "及")
    return (
        len(candidate.attributes) > 1
        or len(candidate.source_spans) > 1
        or any(delimiter in source_text for delimiter in delimiters)
        or len(source_text) > 60
    )


def _fallback_node_shape(
    assertion: ClinicalObjectAssertion,
) -> tuple[FrameNodeType, ContextRole, bool, AtomizationPolicy, str | None]:
    if assertion.assertion_status == ClinicalObjectAssertionStatus.ABSENT:
        return (
            FrameNodeType.NEGATIVE_FINDING,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type in {ClinicalObjectType.SYMPTOM, ClinicalObjectType.SIGN}:
        return (
            FrameNodeType.CLINICAL_OBJECT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type == ClinicalObjectType.FINDING:
        return (
            FrameNodeType.CLINICAL_OBJECT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            "A finding assertion was conservatively mapped to a clinical_object node because no safe parent relation was available in fallback mode.",
        )

    if assertion.object_type == ClinicalObjectType.CARE_SEEKING_OR_MANAGEMENT:
        return (
            FrameNodeType.MANAGEMENT_EVENT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type in {
        ClinicalObjectType.TREATMENT,
        ClinicalObjectType.MEDICATION,
        ClinicalObjectType.PROCEDURE,
    }:
        return (
            FrameNodeType.TREATMENT_EVENT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type == ClinicalObjectType.TREATMENT_RESPONSE:
        return (
            FrameNodeType.TREATMENT_RESPONSE,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type == ClinicalObjectType.ETIOLOGY_OR_TRIGGER:
        return (
            FrameNodeType.TRIGGER_OR_BACKGROUND_CONTEXT,
            ContextRole.INHERITED_CONTEXT,
            False,
            AtomizationPolicy.DO_NOT_GENERATE_CONTEXT_ONLY,
            None,
        )

    if assertion.object_type == ClinicalObjectType.LAB_OR_TEST:
        return (
            FrameNodeType.TEST_OR_MEASUREMENT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    if assertion.object_type == ClinicalObjectType.IMAGING_FINDING:
        return (
            FrameNodeType.CLINICAL_OBJECT,
            ContextRole.LOCAL_CONTENT,
            True,
            AtomizationPolicy.GENERATE_ATOM_WITH_INHERITED_CONTEXT,
            None,
        )

    return (
        FrameNodeType.UNCERTAIN_OR_OTHER,
        ContextRole.UNCERTAIN,
        False,
        AtomizationPolicy.DEFER,
        "An assertion with uncertain or other object type was conservatively mapped to a deferred uncertain_or_other node.",
    )


def _fallback_assertion_status(assertion: ClinicalObjectAssertion) -> NegationStatus:
    if assertion.assertion_status == ClinicalObjectAssertionStatus.ABSENT:
        return NegationStatus.ABSENT
    if assertion.assertion_status in {
        ClinicalObjectAssertionStatus.PRESENT,
        ClinicalObjectAssertionStatus.POSSIBLE,
    }:
        return NegationStatus.PRESENT
    return NegationStatus.UNKNOWN


def _fallback_certainty(
    candidate: AtomizationCandidate,
    assertion: ClinicalObjectAssertion,
) -> CertaintyLevel:
    if assertion.assertion_status == ClinicalObjectAssertionStatus.POSSIBLE:
        return CertaintyLevel.POSSIBLE
    if assertion.assertion_status == ClinicalObjectAssertionStatus.UNCERTAIN:
        return CertaintyLevel.UNCERTAIN
    return _coerce_enum(
        candidate.certainty,
        CertaintyLevel,
        CertaintyLevel.UNKNOWN,
    )


def _coerce_enum(value: Any, enum_type: type, default: Any) -> Any:
    allowed = {item.value: item for item in enum_type}
    if isinstance(value, enum_type):
        return value
    if isinstance(value, str) and value in allowed:
        return allowed[value]
    return default


def _warning(
    *,
    code: str,
    message: str,
    related_item_id: str | None = None,
    severity: ValidationSeverity = ValidationSeverity.WARNING,
) -> AtomizationWarning:
    return AtomizationWarning(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
    )
