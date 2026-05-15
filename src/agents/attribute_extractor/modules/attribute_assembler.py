from __future__ import annotations

from pydantic import ValidationError

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
    AttributeExtractionWarning,
)
from src.schemas.attribute_extractor.attribute_scope import AttributeScope
from src.schemas.attribute_extractor.clinical_attribute import ClinicalAttribute
from src.schemas.attribute_extractor.common import ConfidenceLevel, ValidationSeverity
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

from .attribute_span_validator import AttributeDraftPayload


class AttributeAssembler:
    """Assemble validated and normalized attribute payloads into final schema."""

    def assemble(
        self,
        structuring_result: CaseStructuringResult,
        payload: AttributeDraftPayload,
    ) -> AttributeExtractionResult:
        warnings = list(payload.warnings)
        attributes: list[ClinicalAttribute] = []
        items_by_id = {
            item.item_id: item
            for item in structuring_result.structured_items
        }

        for attribute_payload in payload.attribute_payloads:
            source_item_id = attribute_payload["source_item_id"]
            item = items_by_id.get(source_item_id)
            item_source_text = _item_source_text(item) if item is not None else ""
            attribute_scope = attribute_payload.get("attribute_scope")
            if not attribute_scope:
                warnings.append(
                    AttributeExtractionWarning(
                        severity=ValidationSeverity.WARNING,
                        code="missing_attribute_scope",
                        message=(
                            "Validated attribute payload lacked attribute_scope "
                            "and was assembled with uncertain scope."
                        ),
                        related_item_id=source_item_id,
                    )
                )
                attribute_scope = AttributeScope.UNCERTAIN.value

            data = {
                "case_id": structuring_result.input.case_id,
                "input_id": structuring_result.input.input_id,
                "source_item_id": source_item_id,
                "span_text": attribute_payload["span_text"],
                "attribute_role": attribute_payload["attribute_role"],
                "attribute_scope": attribute_scope,
                "applies_to_text": attribute_payload.get("applies_to_text"),
                "context_text": attribute_payload.get("context_text")
                or item_source_text,
                "source_span": attribute_payload["source_span"],
                "normalized_value": attribute_payload.get("normalized_value"),
                "normalized_unit": attribute_payload.get("normalized_unit"),
                "normalized_text": attribute_payload.get("normalized_text"),
                "extraction_confidence": attribute_payload.get(
                    "extraction_confidence"
                )
                or ConfidenceLevel.MEDIUM.value,
                "notes": attribute_payload.get("notes"),
            }
            try:
                attributes.append(ClinicalAttribute(**data))
            except (TypeError, ValueError, ValidationError):
                warnings.append(
                    AttributeExtractionWarning(
                        severity=ValidationSeverity.WARNING,
                        code="invalid_clinical_attribute",
                        message=(
                            "Validated attribute payload could not be assembled "
                            "into ClinicalAttribute and was skipped."
                        ),
                        related_item_id=attribute_payload.get("source_item_id"),
                    )
                )

        has_error_warning = any(
            warning.severity == ValidationSeverity.ERROR for warning in warnings
        )
        return AttributeExtractionResult(
            case_id=structuring_result.input.case_id,
            input_id=structuring_result.input.input_id,
            source_structuring_result_id=(
                structuring_result.case_structuring_result_id
            ),
            clinical_attributes=attributes,
            extraction_warnings=warnings,
            ready_for_evidence_atomization=not has_error_warning,
        )


def _item_source_text(item: object) -> str:
    source_spans = getattr(item, "source_spans", []) or []
    return "\n".join(span.quoted_text for span in source_spans)
