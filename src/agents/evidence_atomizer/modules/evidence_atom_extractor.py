from __future__ import annotations

from typing import Any

from src.agents.evidence_atomizer.prompting.output_skeletons import (
    evidence_atomization_skeleton,
)
from src.agents.evidence_atomizer.prompting.prompt_context import (
    format_atomization_boundary,
    format_atomization_candidates,
    format_coverage_units,
    format_forbidden_downstream_objects,
)
from src.agents.evidence_atomizer.prompting.schema_contracts import (
    evidence_atomization_contract,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

from .atomization_candidate_builder import AtomizationCandidate
from .base_llm_extractor import BaseLLMExtractor
from .coverage_units import CoverageUnit


class EvidenceAtomExtractor(BaseLLMExtractor):
    """Extract evidence atomization drafts from compact candidates."""

    def extract(
        self,
        structuring_result: CaseStructuringResult,
        candidates: list[AtomizationCandidate],
        coverage_units: list[CoverageUnit],
    ) -> dict[str, Any]:
        candidate_payload = [
            candidate.model_dump(mode="json")
            for candidate in candidates
        ]
        coverage_unit_payload = [
            coverage_unit.model_dump(mode="json")
            for coverage_unit in coverage_units
        ]
        template_vars = {
            **evidence_atomization_contract(),
            "case_id": structuring_result.input.case_id,
            "input_id": structuring_result.input.input_id,
            "stage_id": structuring_result.stage_context.stage_id,
            "case_structuring_result_id": (
                structuring_result.case_structuring_result_id
            ),
            "atomization_boundary": format_atomization_boundary(),
            "forbidden_downstream_objects": format_forbidden_downstream_objects(),
            "atomization_candidates": format_atomization_candidates(candidates),
            "coverage_units": format_coverage_units(coverage_units),
            "output_skeleton": evidence_atomization_skeleton(),
        }

        content = self.generate_json(
            prompt_path=self.prompt_path("evidence_atom_extraction"),
            user_payload={
                "case_id": structuring_result.input.case_id,
                "input_id": structuring_result.input.input_id,
                "stage_id": structuring_result.stage_context.stage_id,
                "case_structuring_result_id": (
                    structuring_result.case_structuring_result_id
                ),
                "atomization_candidates": candidate_payload,
                "coverage_units": coverage_unit_payload,
            },
            instruction=(
                "Return exactly one JSON object with keys evidence_atom_drafts, "
                "item_to_evidence_links, deferred_items, and "
                "atomization_warnings. Every evidence_atom_draft must include "
                "coverage_unit_ids."
            ),
            template_vars=template_vars,
            response_format="json_object",
        )
        payload = self.parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("Evidence atomization draft payload must be a JSON object.")

        for key in (
            "evidence_atom_drafts",
            "item_to_evidence_links",
            "deferred_items",
            "atomization_warnings",
        ):
            if key not in payload:
                payload[key] = []
            if not isinstance(payload[key], list):
                raise ValueError(f"Draft payload key {key!r} must contain an array.")

        return payload
