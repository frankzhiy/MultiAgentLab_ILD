"""EvidenceRelation schema and relation-compatibility table.

Relations are typed semantic links between EvidenceNodes and/or EvidenceFrames.
They replace any tree-style parent/child encoding.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.case_structurer.common import ConfidenceLevel
from src.utils.id_generator import generate_id

from .common import SpanID, normalize_optional_text, require_non_empty_text
from .evidence_frame import EvidenceFrameType
from .evidence_node import EvidenceNodeType


class EvidenceRelationType(StrEnum):
    HAS_TEMPORAL_CONTEXT = "has_temporal_context"
    HAS_NEGATION_SCOPE = "has_negation_scope"
    HAS_CERTAINTY_SCOPE = "has_certainty_scope"
    CO_OCCURS_WITH = "co_occurs_with"
    FINDING_OF = "finding_of"
    PROPERTY_OF = "property_of"
    VALUE_OF = "value_of"
    QUANTITY_OF = "quantity_of"
    SEVERITY_OF = "severity_of"
    LOCATION_OF = "location_of"
    COMPONENT_OF_PANEL = "component_of_panel"
    RESULT_OF_TEST = "result_of_test"
    ABNORMAL_RESULT_OF = "abnormal_result_of"
    NORMAL_RESULT_OF = "normal_result_of"
    REASON_FOR_MANAGEMENT = "reason_for_management"
    CAUSED_BY_OR_ATTRIBUTED_TO = "caused_by_or_attributed_to"
    RESPONSE_TO_TREATMENT = "response_to_treatment"
    CONTRAINDICATES_OR_LIMITS = "contraindicates_or_limits"
    FRAME_REFINES_FRAME = "frame_refines_frame"
    FRAME_REFERENCES_FRAME = "frame_references_frame"


class EvidenceRefType(StrEnum):
    NODE = "node"
    FRAME = "frame"


class EvidenceBasis(StrEnum):
    SOURCE_TEXT = "source_text"
    ASSERTION = "assertion"
    LLM_INFERRED_FROM_ITEM = "llm_inferred_from_item"
    SCHEMA_COMPILED = "schema_compiled"


class EvidenceRelation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    relation_id: str = Field(
        default_factory=lambda: generate_id("evidence_relation")
    )

    source_ref: str
    source_ref_type: EvidenceRefType

    relation_type: EvidenceRelationType

    target_ref: str
    target_ref_type: EvidenceRefType

    evidence_basis: EvidenceBasis
    confidence: ConfidenceLevel
    source_span_ids: list[SpanID] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("source_ref", "target_ref", mode="after")
    @classmethod
    def ref_must_not_be_blank(cls, value: str) -> str:
        return require_non_empty_text(value, "relation endpoint ref")

    @field_validator("notes", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator("source_span_ids", mode="after")
    @classmethod
    def normalize_span_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in value:
            normalized = normalize_optional_text(raw)
            if normalized is None or normalized in cleaned:
                continue
            cleaned.append(normalized)
        return cleaned


# Relation compatibility table. Keys are EvidenceRelationType values. Each
# entry declares which endpoint kinds are valid for that relation. An endpoint
# kind is either:
#   - "node:<EvidenceNodeType.value>" for a specific node type
#   - "node:*" for any node type
#   - "frame:<EvidenceFrameType.value>" for a specific frame type
#   - "frame:*" for any frame type
#
# The validator uses this table to check that each relation's source/target
# endpoint types are allowed.

_NODE_ANY = ("node:*",)
_FRAME_ANY = ("frame:*",)
_NODE_OR_FRAME_ANY = _NODE_ANY + _FRAME_ANY


RELATION_COMPATIBILITY: dict[EvidenceRelationType, dict[str, tuple[str, ...]]] = {
    EvidenceRelationType.HAS_TEMPORAL_CONTEXT: {
        "source": _NODE_OR_FRAME_ANY,
        "target": (f"node:{EvidenceNodeType.TEMPORAL_CONTEXT.value}",),
    },
    EvidenceRelationType.HAS_NEGATION_SCOPE: {
        "source": _NODE_OR_FRAME_ANY,
        "target": (f"node:{EvidenceNodeType.NEGATION_CUE.value}",),
    },
    EvidenceRelationType.HAS_CERTAINTY_SCOPE: {
        "source": _NODE_OR_FRAME_ANY,
        "target": (f"node:{EvidenceNodeType.CERTAINTY_CUE.value}",),
    },
    EvidenceRelationType.CO_OCCURS_WITH: {
        "source": _NODE_OR_FRAME_ANY,
        "target": _NODE_OR_FRAME_ANY,
    },
    EvidenceRelationType.FINDING_OF: {
        "source": _NODE_ANY,
        "target": _NODE_OR_FRAME_ANY,
    },
    EvidenceRelationType.PROPERTY_OF: {
        "source": (f"node:{EvidenceNodeType.OBJECT_PROPERTY.value}",),
        "target": _NODE_ANY,
    },
    EvidenceRelationType.VALUE_OF: {
        "source": _NODE_ANY,
        "target": _NODE_ANY,
    },
    EvidenceRelationType.QUANTITY_OF: {
        "source": (f"node:{EvidenceNodeType.QUANTITY.value}",),
        "target": _NODE_ANY,
    },
    EvidenceRelationType.SEVERITY_OF: {
        "source": (f"node:{EvidenceNodeType.SEVERITY.value}",),
        "target": _NODE_ANY,
    },
    EvidenceRelationType.LOCATION_OF: {
        "source": (f"node:{EvidenceNodeType.LOCATION.value}",),
        "target": _NODE_ANY,
    },
    EvidenceRelationType.COMPONENT_OF_PANEL: {
        "source": _NODE_ANY,
        "target": _FRAME_ANY,
    },
    EvidenceRelationType.RESULT_OF_TEST: {
        "source": (f"node:{EvidenceNodeType.TEST_RESULT.value}",),
        "target": (f"node:{EvidenceNodeType.TEST_NAME.value}",),
    },
    EvidenceRelationType.ABNORMAL_RESULT_OF: {
        "source": (f"node:{EvidenceNodeType.TEST_RESULT.value}",),
        "target": (f"node:{EvidenceNodeType.TEST_NAME.value}",),
    },
    EvidenceRelationType.NORMAL_RESULT_OF: {
        "source": (f"node:{EvidenceNodeType.TEST_RESULT.value}",),
        "target": (f"node:{EvidenceNodeType.TEST_NAME.value}",),
    },
    EvidenceRelationType.REASON_FOR_MANAGEMENT: {
        "source": _NODE_OR_FRAME_ANY,
        "target": (
            f"node:{EvidenceNodeType.MANAGEMENT_EVENT.value}",
            f"node:{EvidenceNodeType.TREATMENT_EVENT.value}",
        ),
    },
    EvidenceRelationType.CAUSED_BY_OR_ATTRIBUTED_TO: {
        "source": _NODE_OR_FRAME_ANY,
        "target": _NODE_OR_FRAME_ANY,
    },
    EvidenceRelationType.RESPONSE_TO_TREATMENT: {
        "source": _NODE_OR_FRAME_ANY,
        "target": (
            f"node:{EvidenceNodeType.TREATMENT_EVENT.value}",
            f"node:{EvidenceNodeType.MANAGEMENT_EVENT.value}",
            *_FRAME_ANY,
        ),
    },
    EvidenceRelationType.CONTRAINDICATES_OR_LIMITS: {
        "source": _NODE_OR_FRAME_ANY,
        "target": _NODE_OR_FRAME_ANY,
    },
    EvidenceRelationType.FRAME_REFINES_FRAME: {
        "source": _FRAME_ANY,
        "target": _FRAME_ANY,
    },
    EvidenceRelationType.FRAME_REFERENCES_FRAME: {
        "source": _FRAME_ANY,
        "target": _FRAME_ANY,
    },
}


def endpoint_kind(ref_type: EvidenceRefType, type_value: str | None) -> str:
    """Build the endpoint kind string used by the compatibility table."""
    base = ref_type.value
    suffix = type_value if type_value else "*"
    return f"{base}:{suffix}"


def is_endpoint_allowed(
    relation_type: EvidenceRelationType,
    side: str,
    endpoint: str,
) -> bool:
    """Check whether the given endpoint kind is allowed on `side`."""
    spec = RELATION_COMPATIBILITY.get(relation_type)
    if spec is None:
        return False
    allowed = spec.get(side, ())
    if endpoint in allowed:
        return True
    ref_type, _, _ = endpoint.partition(":")
    wildcard = f"{ref_type}:*"
    return wildcard in allowed
