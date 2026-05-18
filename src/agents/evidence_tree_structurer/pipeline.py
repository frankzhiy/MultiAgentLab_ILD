"""EvidenceTreeStructurer pipeline.

Flow: structuring_result -> build_item_contexts -> ClinicalAssertionResolver
-> EvidenceTreeBuilder -> EvidenceTreeStructuringResult.
"""

from __future__ import annotations

from collections.abc import Callable
from json import JSONDecodeError
from time import perf_counter
from typing import TYPE_CHECKING, TypeVar

from pydantic import ValidationError

from src.agents.evidence_tree_structurer.errors import (
    EvidenceTreeStructuringParseError,
    EvidenceTreeStructuringPipelineError,
    EvidenceTreeStructuringStepError,
    EvidenceTreeStructuringValidationError,
)
from src.agents.evidence_tree_structurer.result import (
    EvidenceTreeStructuringValidationResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_tree_structurer import TreeStructuringWarning
from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
)
from src.schemas.evidence_tree_structurer.common import (
    TreeStructuringTransformationType,
    ValidationSeverity,
)
from src.schemas.evidence_tree_structurer.evidence_tree import (
    EvidenceTree,
    EvidenceTreeBuildResult,
)
from src.schemas.evidence_tree_structurer.evidence_tree_structuring_result import (
    EvidenceTreeStructuringResult,
)
from src.schemas.evidence_tree_structurer.item_evidence_link import (
    ItemEvidenceTreeLink,
)
from src.validators.evidence_tree_structurer import (
    EvidenceTreeStructuringValidationIssue,
    EvidenceTreeStructuringValidationReport,
)

from .modules import (
    ClinicalAssertionResolver,
    EvidenceTreeBuilder,
    build_item_contexts,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient

T = TypeVar("T")


class EvidenceTreeStructurerPipeline:
    """Tree-first internal pipeline for one public EvidenceTreeStructurerAgent."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_tree_structurer",
    ) -> None:
        if llm_client is None:
            from src.llm.chatanywhere_client import ChatAnywhereClient

            llm_client = ChatAnywhereClient()

        self.llm_client = llm_client
        self.agent_name = agent_name

        self.clinical_assertion_resolver = ClinicalAssertionResolver(
            self.llm_client,
            agent_name=agent_name,
        )
        self.evidence_tree_builder = EvidenceTreeBuilder(
            self.llm_client,
            agent_name=agent_name,
        )

    def run(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceTreeStructuringResult:
        validation_result = self.run_with_validation(
            structuring_result,
            progress_callback=progress_callback,
        )
        if not validation_result.validation_report.accepted:
            raise EvidenceTreeStructuringValidationError(
                step="EvidenceTreeStructuringValidator",
                message="Evidence Tree Structurer validation rejected the result.",
                validation_report=validation_result.validation_report,
            )
        return validation_result.tree_structuring_result

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> EvidenceTreeStructuringValidationResult:
        timings: dict[str, float] = {}

        def run_timed(step: str, func: Callable[[], T]) -> T:
            started_at = perf_counter()
            result = self._run_step(step, func)
            elapsed = perf_counter() - started_at
            timings[step] = elapsed
            if progress_callback is not None:
                progress_callback(step, elapsed)
            return result

        guard_warnings = _check_input(structuring_result)
        if any(w.severity == ValidationSeverity.ERROR for w in guard_warnings):
            tree_structuring_result = EvidenceTreeStructuringResult(
                case_id=structuring_result.input.case_id,
                input_id=structuring_result.input.input_id,
                stage_id=structuring_result.stage_context.stage_id,
                source_structuring_result_id=(
                    structuring_result.case_structuring_result_id
                ),
                evidence_trees=[],
                item_to_tree_links=[],
                deferred_items=[],
                tree_structuring_warnings=guard_warnings,
                ready_for_hypothesis_state=False,
            )
            return EvidenceTreeStructuringValidationResult(
                tree_structuring_result=tree_structuring_result,
                validation_report=_validation_report_from_warnings(guard_warnings),
                clinical_assertion_resolution=ClinicalAssertionResolutionResult(),
                evidence_tree_build_result=EvidenceTreeBuildResult(),
                pipeline_timings_seconds=timings,
            )

        contexts = run_timed(
            "ItemContextBuilder",
            lambda: build_item_contexts(structuring_result),
        )
        assertion_result = run_timed(
            "ClinicalAssertionResolver",
            lambda: self.clinical_assertion_resolver.resolve(contexts),
        )
        tree_build_result = run_timed(
            "EvidenceTreeBuilder",
            lambda: self.evidence_tree_builder.build(
                contexts=contexts,
                assertions=list(assertion_result.clinical_object_assertions),
            ),
        )
        tree_structuring_warnings = [
            *assertion_result.assertion_warnings,
            *tree_build_result.warnings,
        ]

        tree_structuring_result = EvidenceTreeStructuringResult(
            case_id=structuring_result.input.case_id,
            input_id=structuring_result.input.input_id,
            stage_id=structuring_result.stage_context.stage_id,
            source_structuring_result_id=(
                structuring_result.case_structuring_result_id
            ),
            evidence_trees=tree_build_result.evidence_trees,
            item_to_tree_links=_build_item_tree_links(tree_build_result.evidence_trees),
            deferred_items=[],
            tree_structuring_warnings=tree_structuring_warnings,
            ready_for_hypothesis_state=(
                bool(tree_build_result.evidence_trees)
                and not any(
                    w.severity == ValidationSeverity.ERROR
                    for w in tree_structuring_warnings
                )
            ),
        )
        started_at = perf_counter()
        validation_report = _validation_report_from_warnings(
            tree_structuring_result.tree_structuring_warnings,
        )
        elapsed = perf_counter() - started_at
        timings["EvidenceTreeStructuringValidator"] = elapsed
        if progress_callback is not None:
            progress_callback("EvidenceTreeStructuringValidator", elapsed)

        return EvidenceTreeStructuringValidationResult(
            tree_structuring_result=tree_structuring_result,
            validation_report=validation_report,
            clinical_assertion_resolution=assertion_result,
            evidence_tree_build_result=tree_build_result,
            pipeline_timings_seconds=timings,
        )

    @staticmethod
    def _run_step(step: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except EvidenceTreeStructuringPipelineError:
            raise
        except (JSONDecodeError, ValidationError) as exc:
            raise EvidenceTreeStructuringParseError(
                step=step,
                message="Failed to parse or validate pipeline output.",
                original_exception=exc,
            ) from exc
        except Exception as exc:
            raise EvidenceTreeStructuringStepError(
                step=step,
                message="Pipeline step failed.",
                original_exception=exc,
            ) from exc


def _check_input(
    structuring_result: CaseStructuringResult,
) -> list[TreeStructuringWarning]:
    warnings: list[TreeStructuringWarning] = []
    if not structuring_result.ready_for_evidence_tree_structuring:
        warnings.append(
            TreeStructuringWarning(
                severity=ValidationSeverity.ERROR,
                code="structuring_result_not_ready",
                message=(
                    "CaseStructuringResult.ready_for_evidence_tree_structuring is False; "
                    "refusing to build evidence trees."
                ),
            )
        )
    if not structuring_result.structured_items:
        warnings.append(
            TreeStructuringWarning(
                severity=ValidationSeverity.ERROR,
                code="structured_items_empty",
                message="CaseStructuringResult.structured_items is empty.",
            )
        )
    for item in structuring_result.structured_items:
        if not item.source_spans:
            warnings.append(
                TreeStructuringWarning(
                    severity=ValidationSeverity.ERROR,
                    code="structured_item_missing_source_spans",
                    message=(
                        f"StructuredClinicalItem '{item.item_id}' has no source_spans; "
                        "evidence trees require span provenance."
                    ),
                    related_item_id=item.item_id,
                )
            )
    return warnings


def _build_item_tree_links(
    evidence_trees: list[EvidenceTree],
) -> list[ItemEvidenceTreeLink]:
    links: list[ItemEvidenceTreeLink] = []
    for tree in evidence_trees:
        links.append(
            ItemEvidenceTreeLink(
                item_id=tree.source_item_id,
                tree_ids=[tree.tree_id],
                transformation_type=TreeStructuringTransformationType.COPIED,
                explanation=None,
            )
        )
    return links


def _validation_report_from_warnings(
    warnings: list[TreeStructuringWarning],
) -> EvidenceTreeStructuringValidationReport:
    issues = [
        EvidenceTreeStructuringValidationIssue(
            severity=warning.severity,
            code=warning.code,
            message=warning.message,
            related_item_id=warning.related_item_id,
            related_tree_node_id=warning.related_tree_node_id,
            related_span_id=warning.related_span_id,
        )
        for warning in warnings
    ]
    return EvidenceTreeStructuringValidationReport(
        accepted=not any(
            issue.severity == ValidationSeverity.ERROR for issue in issues
        ),
        issues=issues,
    )
