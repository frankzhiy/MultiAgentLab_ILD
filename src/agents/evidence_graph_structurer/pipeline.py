"""Evidence Graph Structurer pipeline.

Flow: CaseStructuringResult
  -> ItemContextBuilder
  -> ClinicalAssertionResolver
  -> EvidenceFrameAssembler
  -> EvidenceRelationExtractor
  -> EvidenceGraphComposer
  -> EvidenceGraphValidator
  -> EvidenceResultAssembler
  -> EvidenceStructuringResult
"""

from __future__ import annotations

from collections.abc import Callable
from json import JSONDecodeError
from time import perf_counter
from typing import TYPE_CHECKING, TypeVar

from pydantic import ValidationError

from src.agents.evidence_graph_structurer.errors import (
    EvidenceGraphStructuringParseError,
    EvidenceGraphStructuringPipelineError,
    EvidenceGraphStructuringStepError,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_graph_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
    ClinicalObjectAssertion,
)
from src.schemas.evidence_graph_structurer.common import ValidationSeverity
from src.schemas.evidence_graph_structurer.evidence_frame import EvidenceFrame
from src.schemas.evidence_graph_structurer.evidence_graph_validation import (
    EvidenceGraphValidationReport,
)
from src.schemas.evidence_graph_structurer.evidence_graphlet import EvidenceGraphlet
from src.schemas.evidence_graph_structurer.evidence_issue import (
    EvidenceStructuringIssue,
)
from src.schemas.evidence_graph_structurer.evidence_structuring_result import (
    EvidenceStructuringResult,
)

from .modules import (
    ClinicalAssertionResolver,
    EvidenceFrameAssembler,
    EvidenceGraphComposer,
    EvidenceGraphValidator,
    EvidenceRelationExtractor,
    EvidenceResultAssembler,
    ItemContext,
    RelationCandidate,
    build_item_contexts,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient

T = TypeVar("T")


class EvidenceGraphStructurerPipeline:
    """Internal pipeline for the public EvidenceGraphStructurerAgent."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_graph_structurer",
    ) -> None:
        if llm_client is None:
            from src.llm.chatanywhere_client import ChatAnywhereClient

            llm_client = ChatAnywhereClient()

        self.llm_client = llm_client
        self.agent_name = agent_name

        self.clinical_assertion_resolver = ClinicalAssertionResolver(
            self.llm_client, agent_name=agent_name
        )
        self.evidence_frame_assembler = EvidenceFrameAssembler(
            self.llm_client, agent_name=agent_name
        )
        self.evidence_relation_extractor = EvidenceRelationExtractor(
            self.llm_client, agent_name=agent_name
        )
        self.evidence_graph_composer = EvidenceGraphComposer()
        self.evidence_graph_validator = EvidenceGraphValidator()
        self.evidence_result_assembler = EvidenceResultAssembler()

    def run(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceStructuringResult:
        timings: dict[str, float] = {}
        structuring_issues: list[EvidenceStructuringIssue] = []

        def run_timed(step: str, func: Callable[[], T]) -> T:
            started_at = perf_counter()
            result = self._run_step(step, func)
            elapsed = perf_counter() - started_at
            timings[step] = elapsed
            if progress_callback is not None:
                progress_callback(step, elapsed)
            return result

        guard_issues = _check_input(structuring_result)
        structuring_issues.extend(guard_issues)
        if any(i.severity is ValidationSeverity.ERROR for i in guard_issues):
            return self.evidence_result_assembler.assemble(
                case_structuring_result=structuring_result,
                assertion_result=ClinicalAssertionResolutionResult(),
                graphlets=[],
                reports=[],
                extra_issues=structuring_issues,
                timings=timings,
            )

        contexts: list[ItemContext] = run_timed(
            "ItemContextBuilder",
            lambda: build_item_contexts(structuring_result),
        )

        assertion_result: ClinicalAssertionResolutionResult = run_timed(
            "ClinicalAssertionResolver",
            lambda: self.clinical_assertion_resolver.resolve(contexts),
        )

        assertions_by_item = _index_assertions(
            assertion_result.clinical_object_assertions
        )

        frame_pair = run_timed(
            "EvidenceFrameAssembler",
            lambda: self.evidence_frame_assembler.assemble(
                contexts, assertions_by_item
            ),
        )
        frames, frame_issues = frame_pair
        structuring_issues.extend(frame_issues)
        frames_by_item = _index_frames(frames)

        relation_pair = run_timed(
            "EvidenceRelationExtractor",
            lambda: self.evidence_relation_extractor.extract(
                contexts, assertions_by_item, frames_by_item
            ),
        )
        candidates, relation_issues = relation_pair
        structuring_issues.extend(relation_issues)
        candidates_by_item = _index_candidates(candidates)

        composer_pair = run_timed(
            "EvidenceGraphComposer",
            lambda: self.evidence_graph_composer.compose(
                contexts,
                assertions_by_item,
                frames_by_item,
                candidates_by_item,
            ),
        )
        graphlets, composer_issues = composer_pair
        structuring_issues.extend(composer_issues)

        contexts_by_item = {ctx.item_id: ctx for ctx in contexts}

        def _validate_all() -> list[EvidenceGraphValidationReport]:
            reports: list[EvidenceGraphValidationReport] = []
            for graphlet in graphlets:
                ctx = contexts_by_item.get(graphlet.source_item_id)
                if ctx is None:
                    continue
                item_assertions = assertions_by_item.get(graphlet.source_item_id, [])
                reports.append(
                    self.evidence_graph_validator.validate(
                        ctx, graphlet, item_assertions
                    )
                )
            return reports

        reports = run_timed("EvidenceGraphValidator", _validate_all)

        result = run_timed(
            "EvidenceResultAssembler",
            lambda: self.evidence_result_assembler.assemble(
                case_structuring_result=structuring_result,
                assertion_result=assertion_result,
                graphlets=graphlets,
                reports=reports,
                extra_issues=structuring_issues,
                timings=timings,
            ),
        )
        return result

    @staticmethod
    def _run_step(step: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except EvidenceGraphStructuringPipelineError:
            raise
        except (JSONDecodeError, ValidationError) as exc:
            raise EvidenceGraphStructuringParseError(
                step=step,
                message="Failed to parse or validate pipeline output.",
                original_exception=exc,
            ) from exc
        except Exception as exc:
            raise EvidenceGraphStructuringStepError(
                step=step,
                message="Pipeline step failed.",
                original_exception=exc,
            ) from exc


def _check_input(
    structuring_result: CaseStructuringResult,
) -> list[EvidenceStructuringIssue]:
    issues: list[EvidenceStructuringIssue] = []
    if not structuring_result.ready_for_evidence_graph_structuring:
        issues.append(
            EvidenceStructuringIssue(
                severity=ValidationSeverity.ERROR,
                code="structuring_result_not_ready",
                message=(
                    "CaseStructuringResult is not ready for evidence graph "
                    "structuring; refusing to run."
                ),
            )
        )
    if not structuring_result.structured_items:
        issues.append(
            EvidenceStructuringIssue(
                severity=ValidationSeverity.ERROR,
                code="structured_items_empty",
                message="CaseStructuringResult.structured_items is empty.",
            )
        )
    for item in structuring_result.structured_items:
        if not item.source_spans:
            issues.append(
                EvidenceStructuringIssue(
                    severity=ValidationSeverity.ERROR,
                    code="structured_item_missing_source_spans",
                    message=(
                        f"StructuredClinicalItem '{item.item_id}' has no "
                        "source_spans; clinical assertion resolution requires "
                        "span provenance."
                    ),
                    related_item_id=item.item_id,
                )
            )
    return issues


def _index_assertions(
    assertions: list[ClinicalObjectAssertion],
) -> dict[str, list[ClinicalObjectAssertion]]:
    grouped: dict[str, list[ClinicalObjectAssertion]] = {}
    for assertion in assertions:
        grouped.setdefault(assertion.source_item_id, []).append(assertion)
    return grouped


def _index_frames(frames: list[EvidenceFrame]) -> dict[str, list[EvidenceFrame]]:
    grouped: dict[str, list[EvidenceFrame]] = {}
    for frame in frames:
        grouped.setdefault(frame.source_item_id, []).append(frame)
    return grouped


def _index_candidates(
    candidates: list[RelationCandidate],
) -> dict[str, list[RelationCandidate]]:
    grouped: dict[str, list[RelationCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.source_item_id, []).append(candidate)
    return grouped
