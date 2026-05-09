from __future__ import annotations

import json

from src.schemas.case_structurer.common import (
    CertaintyLevel,
    ConfidenceLevel,
    NegationStatus,
    TemporalRelation,
)


def stage_context_skeleton(input_id: str, case_id: str, input_order: int) -> str:
    return _format_json(
        {
            "case_id": case_id,
            "input_id": input_id,
            "stage_order": input_order,
            "stage_type": "...",
            "relation_to_previous_stage": "...",
            "previous_stage_id": None,
            "is_initial_stage": input_order == 1,
            "classification_confidence": ConfidenceLevel.MEDIUM.value,
            "classification_basis": "...",
        }
    )


def clinical_section_skeleton(input_id: str) -> str:
    return _format_json(
        {
            "clinical_sections": [
                {
                    "section_id": "section_001",
                    "input_id": input_id,
                    "section_type": "...",
                    "title": None,
                    "normalized_text": "...",
                    "source_spans": [
                        {
                            "span_id": "span_section_001",
                            "input_id": input_id,
                            "quoted_text": "...",
                            "char_start": None,
                            "char_end": None,
                        }
                    ],
                    "section_order": 1,
                    "classification_confidence": ConfidenceLevel.MEDIUM.value,
                    "parent_section_id": None,
                    "notes": None,
                }
            ]
        }
    )


def structured_item_skeleton(input_id: str) -> str:
    return _format_json(
        {
            "structured_items": [
                {
                    "item_id": "item_001",
                    "input_id": input_id,
                    "section_id": "section_001",
                    "item_type": "...",
                    "label": "...",
                    "value": None,
                    "unit": None,
                    "body_site": None,
                    "temporality": TemporalRelation.UNKNOWN.value,
                    "time_text": None,
                    "certainty": CertaintyLevel.DEFINITE.value,
                    "negation": NegationStatus.PRESENT.value,
                    "source_spans": [
                        {
                            "span_id": "span_item_001",
                            "input_id": input_id,
                            "quoted_text": "...",
                            "char_start": None,
                            "char_end": None,
                        }
                    ],
                    "item_order": 1,
                    "classification_confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ]
        }
    )


def temporal_ambiguity_skeleton(input_id: str) -> str:
    return _format_json(
        {
            "timeline_events": [
                {
                    "event_id": "event_001",
                    "input_id": input_id,
                    "event_type": "...",
                    "event_time_text": "...",
                    "time_expression_type": "...",
                    "normalized_time": None,
                    "relative_time": None,
                    "description": "...",
                    "related_item_ids": ["item_001"],
                    "source_spans": [
                        {
                            "span_id": "span_event_001",
                            "input_id": input_id,
                            "quoted_text": "...",
                            "char_start": None,
                            "char_end": None,
                        }
                    ],
                    "event_order": 1,
                    "classification_confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
            "ambiguities": [
                {
                    "ambiguity_id": "ambiguity_001",
                    "input_id": input_id,
                    "ambiguity_type": "...",
                    "ambiguous_text": "...",
                    "possible_interpretations": ["..."],
                    "reason": "...",
                    "related_section_ids": ["section_001"],
                    "related_item_ids": ["item_001"],
                    "source_spans": [
                        {
                            "span_id": "span_ambiguity_001",
                            "input_id": input_id,
                            "quoted_text": "...",
                            "char_start": None,
                            "char_end": None,
                        }
                    ],
                    "needs_clarification": True,
                    "classification_confidence": ConfidenceLevel.MEDIUM.value,
                    "notes": None,
                }
            ],
        }
    )


def _format_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
