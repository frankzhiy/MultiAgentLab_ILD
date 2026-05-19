"""EvidenceTreeStructurer pipeline.

Flow: structuring_result -> build_item_contexts -> ClinicalAssertionResolver.
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
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_tree_structurer import TreeStructuringWarning
from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
)
from src.schemas.evidence_tree_structurer.common import ValidationSeverity

from .modules import (
    ClinicalAssertionResolver,
    build_item_contexts,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient

T = TypeVar("T")


class EvidenceTreeStructurerPipeline:
    """Internal pipeline for one public EvidenceTreeStructurerAgent."""

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

    def run(
        self,
        structuring_result: CaseStructuringResult,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> ClinicalAssertionResolutionResult:
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
            return ClinicalAssertionResolutionResult()

        contexts = run_timed(
            "ItemContextBuilder",
            lambda: build_item_contexts(structuring_result),
        )
        assertion_result = run_timed(
            "ClinicalAssertionResolver",
            lambda: self.clinical_assertion_resolver.resolve(contexts),
        )
        return assertion_result

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
                    "refusing to run clinical assertion resolution."
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
                        "clinical assertion resolution requires span provenance."
                    ),
                    related_item_id=item.item_id,
                )
            )
    return warnings
