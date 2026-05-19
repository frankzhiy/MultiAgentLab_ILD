"""EvidenceGraphlet schema.

An EvidenceGraphlet is one local clinical evidence graph that belongs to a
single source item. It contains frames, nodes, and typed relations.

It is NOT a strict tree. Display code may render the graphlet as a tree-like
view, but the stored data model is frames + nodes + relations.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.utils.id_generator import generate_id

from .common import ItemID, SpanID, normalize_optional_text
from .evidence_frame import EvidenceFrame
from .evidence_node import EvidenceNode
from .evidence_relation import EvidenceRelation


class EvidenceGraphletStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class EvidenceGraphlet(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    graphlet_id: str = Field(
        default_factory=lambda: generate_id("evidence_graphlet")
    )
    source_item_id: ItemID

    source_span_ids: list[SpanID] = Field(default_factory=list)

    frames: list[EvidenceFrame] = Field(default_factory=list)
    nodes: list[EvidenceNode] = Field(default_factory=list)
    relations: list[EvidenceRelation] = Field(default_factory=list)

    status: EvidenceGraphletStatus = EvidenceGraphletStatus.NEEDS_REVIEW
    validation_report_id: str | None = None

    display_hints: dict[str, object] = Field(
        default_factory=dict,
        description=(
            "Free-form hints for downstream renderers. May suggest a "
            "tree-like view but does not change the stored data model."
        ),
    )

    @classmethod
    def empty(cls, source_item_id: str) -> "EvidenceGraphlet":
        return cls(source_item_id=source_item_id)

    def normalized_validation_report_id(self) -> str | None:
        return normalize_optional_text(self.validation_report_id)
