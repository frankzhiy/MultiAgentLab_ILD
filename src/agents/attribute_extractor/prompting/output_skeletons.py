from __future__ import annotations

import json

from src.schemas.attribute_extractor.attribute_role import AttributeRole
from src.schemas.attribute_extractor.common import ConfidenceLevel, ValidationSeverity


def attribute_span_role_labeling_skeleton() -> str:
    return json.dumps(
        {
            "attribute_spans": [
                {
                    "source_item_id": "item_001",
                    "span_text": "...",
                    "attribute_role": AttributeRole.OTHER_ATTRIBUTE.value,
                    "normalized_value": None,
                    "normalized_unit": None,
                    "normalized_text": None,
                    "extraction_confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
            "extraction_warnings": [
                {
                    "severity": ValidationSeverity.WARNING.value,
                    "code": "attribute_extraction_uncertain",
                    "message": "...",
                    "related_item_id": "item_001",
                    "related_attribute_id": None,
                }
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
