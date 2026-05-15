from __future__ import annotations

from collections.abc import Callable
from json import JSONDecodeError
from typing import TYPE_CHECKING
from typing import TypeVar

from pydantic import ValidationError

from src.agents.evidence_atomizer.errors import (
    EvidenceAtomizationParseError,
    EvidenceAtomizationPipelineError,
    EvidenceAtomizationStepError,
    EvidenceAtomizationValidationError,
)
from src.agents.evidence_atomizer.result import EvidenceAtomizationValidationResult
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult
from src.schemas.evidence_atomizer.common import ValidationSeverity
from src.schemas.evidence_atomizer.evidence_atomization_result import (
    EvidenceAtomizationResult,
)
from src.validators.evidence_atomizer import (
    EvidenceAtomizationValidationIssue,
    EvidenceAtomizationValidationReport,
    EvidenceAtomizationValidator,
)
from src.validators.evidence_atomizer.evidence_atomization_coverage_validator import (
    CoverageValidationResult,
    EvidenceAtomizationCoverageValidator,
)

from .modules import (
    AtomizationCandidateBuilder,
    ClinicalAssertionResolver,
    EvidenceAtomDeduplicator,
    EvidenceAtomExtractor,
    EvidenceAtomizationAssembler,
    EvidenceAtomizerInputGuard,
    EvidenceAtomNormalizer,
    EvidenceEventFrameBuilder,
    FrameAwareCoverageUnitBuilder,
)
from src.schemas.evidence_atomizer import AtomizationWarning
from src.schemas.evidence_atomizer.clinical_object_assertion import (
    ClinicalAssertionResolutionResult,
)
from src.schemas.evidence_atomizer.evidence_event_frame import (
    EvidenceEventFrameBuildResult,
)

if TYPE_CHECKING:
    from src.llm.chatanywhere_client import ChatAnywhereClient

T = TypeVar("T")


class EvidenceAtomizerPipeline:
    """Hybrid internal pipeline for one public EvidenceAtomizerAgent."""

    def __init__(
        self,
        llm_client: ChatAnywhereClient | None = None,
        agent_name: str = "evidence_atomizer",
    ) -> None:
        if llm_client is None:
            from src.llm.chatanywhere_client import ChatAnywhereClient

            llm_client = ChatAnywhereClient()

        self.llm_client = llm_client
        self.agent_name = agent_name

        self.input_guard = EvidenceAtomizerInputGuard()
        self.candidate_builder = AtomizationCandidateBuilder()
        self.clinical_assertion_resolver = ClinicalAssertionResolver(
            self.llm_client,
            agent_name=agent_name,
        )
        self.evidence_event_frame_builder = EvidenceEventFrameBuilder(
            self.llm_client,
            agent_name=agent_name,
        )
        self.coverage_unit_builder = FrameAwareCoverageUnitBuilder()
        self.evidence_atom_extractor = EvidenceAtomExtractor(
            self.llm_client,
            agent_name=agent_name,
        )
        self.evidence_atom_normalizer = EvidenceAtomNormalizer()
        self.evidence_atom_deduplicator = EvidenceAtomDeduplicator()
        self.assembler = EvidenceAtomizationAssembler()
        self.coverage_validator = EvidenceAtomizationCoverageValidator()
        self.validator = EvidenceAtomizationValidator()

    def run(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
    ) -> EvidenceAtomizationResult:
        validation_result = self.run_with_validation(
            structuring_result,
            attribute_result,
        )
        if not validation_result.validation_report.accepted:
            raise EvidenceAtomizationValidationError(
                step="EvidenceAtomizationValidator",
                message="Evidence Atomizer validation rejected the result.",
                validation_report=validation_result.validation_report,
            )
        return validation_result.atomization_result

    def run_with_validation(
        self,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
    ) -> EvidenceAtomizationValidationResult:
        guard_warnings = self._run_step(
            "EvidenceAtomizerInputGuard",
            lambda: self.input_guard.check(structuring_result, attribute_result),
        )

        if _has_error_warning(guard_warnings):
            atomization_result = self._run_step(
                "GuardedEvidenceAtomizationResult",
                lambda: EvidenceAtomizationResult(
                    case_id=structuring_result.input.case_id,
                    input_id=structuring_result.input.input_id,
                    stage_id=structuring_result.stage_context.stage_id,
                    source_structuring_result_id=(
                        structuring_result.case_structuring_result_id
                    ),
                    evidence_atoms=[],
                    item_to_evidence_links=[],
                    deferred_items=[],
                    atomization_warnings=guard_warnings,
                    ready_for_hypothesis_state=False,
                ),
            )
            validation_report = self._run_step(
                "EvidenceAtomizationValidator",
                lambda: self.validator.validate(
                    structuring_result=structuring_result,
                    attribute_result=attribute_result,
                    atomization_result=atomization_result,
                ),
            )
            return EvidenceAtomizationValidationResult(
                atomization_result=atomization_result,
                validation_report=validation_report,
                clinical_assertion_resolution=ClinicalAssertionResolutionResult(),
                evidence_event_frame_build_result=EvidenceEventFrameBuildResult(),
            )

        candidates = self._run_step(
            "AtomizationCandidateBuilder",
            lambda: self.candidate_builder.build(
                structuring_result,
                attribute_result,
            ),
        )
        assertion_result = self._run_step(
            "ClinicalAssertionResolver",
            lambda: self.clinical_assertion_resolver.resolve(candidates),
        )
        frame_build_result = self._run_step(
            "EvidenceEventFrameBuilder",
            lambda: self.evidence_event_frame_builder.build(
                candidates=candidates,
                assertions=assertion_result.clinical_object_assertions,
            ),
        )
        coverage_build_result = self._run_step(
            "FrameAwareCoverageUnitBuilder",
            lambda: self.coverage_unit_builder.build(
                candidates=candidates,
                assertions=assertion_result.clinical_object_assertions,
                frames=frame_build_result.frames,
            ),
        )
        coverage_units = coverage_build_result.coverage_units
        draft_payload = self._run_step(
            "EvidenceAtomExtractor",
            lambda: self.evidence_atom_extractor.extract(
                structuring_result,
                attribute_result,
                candidates,
                coverage_units,
            ),
        )
        normalized_payload = self._run_step(
            "EvidenceAtomNormalizer",
            lambda: self.evidence_atom_normalizer.normalize(
                structuring_result,
                attribute_result,
                candidates,
                coverage_units,
                draft_payload,
            ),
        )
        normalized_payload = self._run_step(
            "EvidenceAtomDeduplicator",
            lambda: self.evidence_atom_deduplicator.deduplicate(
                normalized_payload=normalized_payload,
                coverage_units=coverage_units,
            ),
        )
        normalized_payload = normalized_payload.model_copy(
            update={
                "atomization_warnings": _merge_atomization_warnings(
                    normalized_payload.atomization_warnings,
                    assertion_result.assertion_warnings,
                    frame_build_result.warnings,
                    coverage_build_result.warnings,
                ),
            }
        )
        atomization_result = self._run_step(
            "EvidenceAtomizationAssembler",
            lambda: self.assembler.assemble(
                structuring_result,
                attribute_result,
                normalized_payload,
            ),
        )
        coverage_validation = self._run_step(
            "EvidenceAtomizationCoverageValidator",
            lambda: self.coverage_validator.validate(
                coverage_units=coverage_units,
                evidence_id_to_coverage_unit_ids=(
                    normalized_payload.evidence_id_to_coverage_unit_ids
                ),
                atomization_result=atomization_result,
            ),
        )
        validation_report = self._run_step(
            "EvidenceAtomizationValidator",
            lambda: self.validator.validate(
                structuring_result=structuring_result,
                attribute_result=attribute_result,
                atomization_result=atomization_result,
            ),
        )
        validation_report = _merge_coverage_validation(
            validation_report,
            coverage_validation,
        )
        return EvidenceAtomizationValidationResult(
            atomization_result=atomization_result,
            validation_report=validation_report,
            clinical_assertion_resolution=assertion_result,
            evidence_event_frame_build_result=frame_build_result,
        )

    @staticmethod
    def _run_step(step: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except EvidenceAtomizationPipelineError:
            raise
        except (JSONDecodeError, ValidationError) as exc:
            raise EvidenceAtomizationParseError(
                step=step,
                message="Failed to parse or validate pipeline output.",
                original_exception=exc,
            ) from exc
        except Exception as exc:
            raise EvidenceAtomizationStepError(
                step=step,
                message="Pipeline step failed.",
                original_exception=exc,
            ) from exc


def _has_error_warning(warnings: list[object]) -> bool:
    return any(
        getattr(warning, "severity", None) == ValidationSeverity.ERROR
        for warning in warnings
    )


def _merge_coverage_validation(
    validation_report: EvidenceAtomizationValidationReport,
    coverage_validation: CoverageValidationResult,
) -> EvidenceAtomizationValidationReport:
    issues = [
        *validation_report.issues,
        *[
            EvidenceAtomizationValidationIssue(
                severity=issue.severity,
                code=issue.code,
                message=_coverage_issue_message(issue.message, issue.related_coverage_unit_id),
                related_item_id=issue.related_item_id,
                related_evidence_id=issue.related_evidence_id,
                related_span_id=None,
            )
            for issue in coverage_validation.issues
        ],
    ]
    return EvidenceAtomizationValidationReport(
        accepted=not any(
            issue.severity == ValidationSeverity.ERROR for issue in issues
        ),
        issues=issues,
    )


def _coverage_issue_message(
    message: str,
    coverage_unit_id: str | None,
) -> str:
    if coverage_unit_id is None:
        return message
    return f"{message} [coverage_unit_id={coverage_unit_id}]"


def _merge_atomization_warnings(
    existing_warnings: list[AtomizationWarning],
    assertion_warnings: list[AtomizationWarning],
    frame_build_warnings: list[AtomizationWarning],
    coverage_build_warnings: list[AtomizationWarning | str],
) -> list[AtomizationWarning]:
    warnings = [*existing_warnings, *assertion_warnings, *frame_build_warnings]
    for warning in coverage_build_warnings:
        if isinstance(warning, AtomizationWarning):
            warnings.append(warning)
            continue
        warnings.append(
            AtomizationWarning(
                severity=ValidationSeverity.WARNING,
                code="coverage_unit_builder_warning",
                message=str(warning),
            )
        )
    return warnings
