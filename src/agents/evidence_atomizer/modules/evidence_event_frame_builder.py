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

            draft_payload = self._build_candidate_payload(
                candidate,
                assertions_by_item_id.get(candidate.item_id, []),
            )
            frame, frame_warnings = self.validator.validate(
                candidate=candidate,
                draft_payload=draft_payload,
            )
            warnings.extend(frame_warnings)

            if frame is None:
                fallback_frame = _fallback_frame(candidate)
                if fallback_frame is not None:
                    frames.append(fallback_frame)
                    warnings.append(
                        _warning(
                            code="frame_builder_fallback_used",
                            message="A conservative single-node EvidenceEventFrame fallback was used after draft validation failed.",
                            related_item_id=candidate.item_id,
                        )
                    )
                continue

            frames.append(frame)

        return EvidenceEventFrameBuildResult(frames=frames, warnings=warnings)

    def _build_candidate_payload(
        self,
        candidate: AtomizationCandidate,
        assertions: list[ClinicalObjectAssertion],
    ) -> dict[str, Any]:
        template_vars = {
            "atomization_boundary": format_atomization_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "atomization_candidate": format_atomization_candidates([candidate]),
            "clinical_object_assertions": _format_assertions(assertions),
            "output_skeleton": _frame_output_skeleton(candidate.item_id),
        }
        content = self.generate_json(
            prompt_path=self.prompt_path("evidence_event_frame_building"),
            user_payload={
                "atomization_candidate": candidate.model_dump(mode="json"),
                "clinical_object_assertions": [
                    assertion.model_dump(mode="json")
                    for assertion in assertions
                ],
            },
            instruction=(
                "Return exactly one JSON object with keys frame_nodes and "
                "frame_warnings for this single atomization candidate."
            ),
            template_vars=template_vars,
            response_format="json_object",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("EvidenceEventFrame draft payload must be a JSON object.")
        if "frame_nodes" not in payload:
            payload["frame_nodes"] = []
        if "frame_warnings" not in payload:
            payload["frame_warnings"] = []
        return payload


def _fallback_frame(candidate: AtomizationCandidate) -> EvidenceEventFrame | None:
    source_text = candidate.source_text.strip()
    if not source_text:
        return None

    node = EvidenceFrameNode(
        source_item_id=candidate.item_id,
        node_type=FrameNodeType.MAIN_EVENT,
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
        source_attribute_ids=[attribute.attribute_id for attribute in candidate.attributes],
        source_span_ids=[
            span_id
            for span in candidate.source_spans
            if isinstance((span_id := span.get("span_id")), str) and span_id.strip()
        ],
    )
    return EvidenceEventFrame(
        frame_id=generate_evidence_frame_id(),
        source_item_id=candidate.item_id,
        source_text=source_text,
        frame_nodes=[node],
        frame_warnings=[
            _warning(
                code="frame_builder_fallback_used",
                message="EvidenceEventFrame fallback contains only the full source statement as a main_event node.",
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
        '      "node_type": "main_event",\n'
        '      "node_text": "...",\n'
        '      "assertion_status": "present",\n'
        '      "certainty": "definite",\n'
        '      "temporality": "unknown",\n'
        '      "parent_node_id": null,\n'
        '      "relation_to_parent": null,\n'
        '      "inherited_context_node_ids": [],\n'
        '      "source_attribute_ids": [],\n'
        '      "source_span_ids": [],\n'
        '      "context_role": "local_content",\n'
        '      "atomizable": true,\n'
        '      "atomization_policy": "generate_atom_with_inherited_context",\n'
        '      "confidence": "medium",\n'
        '      "notes": null\n'
        "    }\n"
        "  ],\n"
        '  "frame_warnings": []\n'
        "}"
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
