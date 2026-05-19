"""EvidenceStructuringResult schema.

Final assembled output of the Evidence Graph Structurer pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.utils.id_generator import generate_id

from .clinical_object_assertion import ClinicalObjectAssertion
from .common import CaseID, InputID, StageID
from .evidence_graph_validation import EvidenceGraphValidationReport
from .evidence_graphlet import EvidenceGraphlet
from .evidence_issue import EvidenceStructuringIssue


class EvidenceStructuringResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    evidence_structuring_result_id: str = Field(
        default_factory=lambda: generate_id("evidence_structuring_result")
    )

    case_id: CaseID
    input_id: InputID
    stage_id: StageID | None = None
    source_structuring_result_id: str | None = None

    clinical_object_assertions: list[ClinicalObjectAssertion] = Field(
        default_factory=list
    )
    assertion_issues: list[EvidenceStructuringIssue] = Field(default_factory=list)

    graphlets: list[EvidenceGraphlet] = Field(default_factory=list)
    validation_reports: list[EvidenceGraphValidationReport] = Field(
        default_factory=list
    )

    structuring_issues: list[EvidenceStructuringIssue] = Field(default_factory=list)

    ready_for_hypothesis_state: bool = False

    timings: dict[str, float] = Field(default_factory=dict)
