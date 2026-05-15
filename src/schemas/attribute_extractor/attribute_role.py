"""Attribute roles produced by target-grounded attribute labeling."""

from __future__ import annotations

from enum import StrEnum


class AttributeRole(StrEnum):
    """Semantic role played by a source-copied attribute modifier span."""

    AGE = "age"
    SEX = "sex"

    SYMPTOM_DURATION = "symptom_duration"
    DISEASE_HISTORY_DURATION = "disease_history_duration"
    WORSENING_INTERVAL = "worsening_interval"
    ONSET_TIME = "onset_time"

    NUMERIC_RESULT = "numeric_result"
    QUALITATIVE_RESULT = "qualitative_result"
    MEASUREMENT_UNIT = "measurement_unit"
    ABNORMAL_DIRECTION = "abnormal_direction"

    MEDICATION_DOSE = "medication_dose"
    MEDICATION_FREQUENCY = "medication_frequency"
    MEDICATION_ROUTE = "medication_route"

    BODY_SITE = "body_site"

    OTHER_ATTRIBUTE = "other_attribute"
    UNCERTAIN_ATTRIBUTE = "uncertain_attribute"
