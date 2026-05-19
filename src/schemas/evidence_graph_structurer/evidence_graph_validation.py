"""EvidenceGraphValidationReport schema."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.utils.id_generator import generate_id

from .common import ItemID
from .evidence_issue import EvidenceStructuringIssue


class EvidenceGraphValidationStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class EvidenceGraphValidationReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    validation_report_id: str = Field(
        default_factory=lambda: generate_id("evidence_graph_validation_report")
    )
    source_item_id: ItemID
    graphlet_id: str

    status: EvidenceGraphValidationStatus

    issues: list[EvidenceStructuringIssue] = Field(default_factory=list)

    assertion_coverage: dict[str, object] = Field(
        default_factory=dict,
        description=(
            "Summary of how the input ClinicalObjectAssertions are covered by "
            "nodes, frames, or explicit issues. e.g. {'total': N, 'covered': K, "
            "'uncovered_assertion_ids': [...]}."
        ),
    )

    frame_coverage: dict[str, object] = Field(
        default_factory=dict,
        description=(
            "Summary of which frames are populated. e.g. {'total': N, 'empty': M, "
            "'empty_frame_ids': [...]}."
        ),
    )

    relation_checks: dict[str, object] = Field(
        default_factory=dict,
        description=(
            "Summary of relation-vocabulary and endpoint-compatibility checks. "
            "e.g. {'total': N, 'invalid_type': K, 'incompatible_endpoints': M, ...}."
        ),
    )

    downstream_readiness: bool = Field(
        default=False,
        description=(
            "True only if the accepted graphlet is safe to pass to the later "
            "hypothesis state layer. False if any error-level issue is present."
        ),
    )
