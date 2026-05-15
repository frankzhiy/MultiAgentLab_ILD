from __future__ import annotations

from src.agents.attribute_extractor.result import (
    AttributeExtractionValidationIssue,
    AttributeExtractionValidationReport,
)
from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionResult,
)
from src.schemas.attribute_extractor.common import (
    AttributeID,
    ItemID,
    ValidationSeverity,
)
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult


class AttributeExtractionValidator:
    """Validate AttributeExtractionResult against CaseStructuringResult."""

    def validate(
        self,
        *,
        structuring_result: CaseStructuringResult,
        attribute_result: AttributeExtractionResult,
    ) -> AttributeExtractionValidationReport:
        issues: list[AttributeExtractionValidationIssue] = []
        items_by_id = {
            item.item_id: item
            for item in structuring_result.structured_items
        }

        if attribute_result.case_id != structuring_result.input.case_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="case_id_mismatch",
                    message=(
                        "AttributeExtractionResult.case_id must match "
                        "CaseStructuringResult.input.case_id."
                    ),
                )
            )

        if attribute_result.input_id != structuring_result.input.input_id:
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="input_id_mismatch",
                    message=(
                        "AttributeExtractionResult.input_id must match "
                        "CaseStructuringResult.input.input_id."
                    ),
                )
            )

        if (
            attribute_result.source_structuring_result_id
            != structuring_result.case_structuring_result_id
        ):
            issues.append(
                _issue(
                    severity=ValidationSeverity.ERROR,
                    code="source_structuring_result_id_mismatch",
                    message=(
                        "AttributeExtractionResult.source_structuring_result_id "
                        "must match CaseStructuringResult.case_structuring_result_id."
                    ),
                )
            )

        for attribute in attribute_result.clinical_attributes:
            item = items_by_id.get(attribute.source_item_id)
            if item is None:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="missing_source_item",
                        message=(
                            "ClinicalAttribute.source_item_id must reference an "
                            "existing StructuredClinicalItem.item_id."
                        ),
                        related_item_id=attribute.source_item_id,
                        related_attribute_id=attribute.attribute_id,
                    )
                )
                continue

            item_source_text = "\n".join(span.quoted_text for span in item.source_spans)
            if attribute.span_text not in item_source_text:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="attribute_span_not_in_source_item",
                        message=(
                            "ClinicalAttribute.span_text must be present in its "
                            "source item's source text."
                        ),
                        related_item_id=attribute.source_item_id,
                        related_attribute_id=attribute.attribute_id,
                    )
                )
            if attribute.source_span.quoted_text != attribute.span_text:
                issues.append(
                    _issue(
                        severity=ValidationSeverity.ERROR,
                        code="attribute_source_span_text_mismatch",
                        message=(
                            "ClinicalAttribute.source_span.quoted_text must equal "
                            "ClinicalAttribute.span_text."
                        ),
                        related_item_id=attribute.source_item_id,
                        related_attribute_id=attribute.attribute_id,
                    )
                )

        return AttributeExtractionValidationReport(
            accepted=not any(
                issue.severity == ValidationSeverity.ERROR for issue in issues
            ),
            issues=issues,
        )


def _issue(
    *,
    severity: ValidationSeverity,
    code: str,
    message: str,
    related_item_id: ItemID | None = None,
    related_attribute_id: AttributeID | None = None,
) -> AttributeExtractionValidationIssue:
    return AttributeExtractionValidationIssue(
        severity=severity,
        code=code,
        message=message,
        related_item_id=related_item_id,
        related_attribute_id=related_attribute_id,
    )
