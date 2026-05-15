from __future__ import annotations

from src.schemas.attribute_extractor.attribute_extraction_result import (
    AttributeExtractionWarning,
)
from src.schemas.attribute_extractor.attribute_role import AttributeRole
from src.schemas.attribute_extractor.common import ValidationSeverity
from src.schemas.case_structurer.case_structuring_result import CaseStructuringResult

from .attribute_span_validator import AttributeDraftPayload


ALLOWED_ROLES_BY_ITEM_TYPE: dict[str, set[AttributeRole]] = {
    "demographic": {
        AttributeRole.AGE,
        AttributeRole.SEX,
        AttributeRole.SYMPTOM_DURATION,
        AttributeRole.ONSET_TIME,
        AttributeRole.WORSENING_INTERVAL,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "symptom": {
        AttributeRole.SYMPTOM_DURATION,
        AttributeRole.ONSET_TIME,
        AttributeRole.WORSENING_INTERVAL,
        AttributeRole.BODY_SITE,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "sign": {
        AttributeRole.BODY_SITE,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "diagnosis_history": {
        AttributeRole.DISEASE_HISTORY_DURATION,
        AttributeRole.ONSET_TIME,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.MEDICATION_DOSE,
        AttributeRole.MEDICATION_FREQUENCY,
        AttributeRole.MEDICATION_ROUTE,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "comorbidity": {
        AttributeRole.DISEASE_HISTORY_DURATION,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.MEDICATION_DOSE,
        AttributeRole.MEDICATION_FREQUENCY,
        AttributeRole.MEDICATION_ROUTE,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "lab_result": {
        AttributeRole.NUMERIC_RESULT,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.MEASUREMENT_UNIT,
        AttributeRole.ABNORMAL_DIRECTION,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "pulmonary_function": {
        AttributeRole.NUMERIC_RESULT,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.MEASUREMENT_UNIT,
        AttributeRole.ABNORMAL_DIRECTION,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "imaging_finding": {
        AttributeRole.ONSET_TIME,
        AttributeRole.BODY_SITE,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.ABNORMAL_DIRECTION,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "pathology_finding": {
        AttributeRole.BODY_SITE,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.ABNORMAL_DIRECTION,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "medication": {
        AttributeRole.MEDICATION_DOSE,
        AttributeRole.MEDICATION_FREQUENCY,
        AttributeRole.MEDICATION_ROUTE,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "procedure": {
        AttributeRole.ONSET_TIME,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "treatment": {
        AttributeRole.MEDICATION_DOSE,
        AttributeRole.MEDICATION_FREQUENCY,
        AttributeRole.MEDICATION_ROUTE,
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "treatment_response": {
        AttributeRole.QUALITATIVE_RESULT,
        AttributeRole.ABNORMAL_DIRECTION,
        AttributeRole.OTHER_ATTRIBUTE,
        AttributeRole.UNCERTAIN_ATTRIBUTE,
    },
    "other": {AttributeRole.OTHER_ATTRIBUTE, AttributeRole.UNCERTAIN_ATTRIBUTE},
    "uncertain": {AttributeRole.OTHER_ATTRIBUTE, AttributeRole.UNCERTAIN_ATTRIBUTE},
}


class RoleConstraintValidator:
    """Constrain attribute roles based on source item type without re-reasoning."""

    def validate(
        self,
        structuring_result: CaseStructuringResult,
        payload: AttributeDraftPayload,
    ) -> AttributeDraftPayload:
        warnings = list(payload.warnings)
        items_by_id = {
            item.item_id: item
            for item in structuring_result.structured_items
        }
        constrained_payloads: list[dict] = []

        for attribute in payload.attribute_payloads:
            source_item_id = attribute["source_item_id"]
            item = items_by_id[source_item_id]
            item_type = getattr(item.item_type, "value", str(item.item_type))
            role = _coerce_role(attribute.get("attribute_role"))
            allowed_roles = ALLOWED_ROLES_BY_ITEM_TYPE.get(
                item_type,
                ALLOWED_ROLES_BY_ITEM_TYPE["uncertain"],
            )
            if role not in allowed_roles:
                warnings.append(
                    AttributeExtractionWarning(
                        severity=ValidationSeverity.WARNING,
                        code="attribute_role_not_allowed_for_item_type",
                        message=(
                            "Attribute role is not allowed for source item type "
                            "and was changed to uncertain_attribute."
                        ),
                        related_item_id=source_item_id,
                    )
                )
                role = AttributeRole.UNCERTAIN_ATTRIBUTE

            constrained_payload = dict(attribute)
            constrained_payload["attribute_role"] = role.value
            constrained_payloads.append(constrained_payload)

        return AttributeDraftPayload(
            attribute_payloads=constrained_payloads,
            warnings=warnings,
        )


def _coerce_role(value: object) -> AttributeRole:
    if isinstance(value, AttributeRole):
        return value
    if isinstance(value, str):
        for role in AttributeRole:
            if value == role.value:
                return role
    return AttributeRole.UNCERTAIN_ATTRIBUTE
