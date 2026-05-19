"""Schema-contract snippets injected into LLM prompts."""

from __future__ import annotations

from src.schemas.evidence_tree_structurer.clinical_object_assertion import (
    ClinicalObjectAssertionStatus,
    ClinicalObjectType,
)
from src.schemas.evidence_tree_structurer.common import (
    ConfidenceLevel,
    ValidationSeverity,
)


def clinical_object_assertion_fields() -> str:
    rows = [
        ("source_item_id", "str", "Must equal the item_id of the input item."),
        ("object_text", "str", "Exact substring of source_text."),
        (
            "object_type",
            "enum",
            ", ".join(
                value.value
                for value in ClinicalObjectType
                if value is not ClinicalObjectType.UNCERTAIN
            ),
        ),
        (
            "assertion_status",
            "enum",
            ", ".join(value.value for value in ClinicalObjectAssertionStatus),
        ),
        ("assertion_cue_text", "str|null", "Source-copied cue word (e.g. 出现, 否认, 无)."),
        ("assertion_scope_text", "str|null", "Source-copied scope phrase covering the object."),
        (
            "temporal_anchor_text",
            "str|null",
            "Source-copied time anchor scoping this assertion (e.g. 10天前, 入院当日).",
        ),
        (
            "trigger_text",
            "str|null",
            "Source-copied trigger/cause phrase (e.g. 受凉后, 无明显诱因).",
        ),
        (
            "modifier_texts",
            "list[str]",
            "Source-copied modifier phrases attached to this assertion.",
        ),
        (
            "confidence",
            "enum",
            ", ".join(value.value for value in ConfidenceLevel),
        ),
        ("notes", "str|null", "Optional short note; no inferred clinical reasoning."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)


def assertion_warning_fields() -> str:
    rows = [
        ("severity", "enum", ", ".join(value.value for value in ValidationSeverity)),
        ("code", "str", "Short snake_case code, e.g. assertion_needs_review."),
        ("message", "str", "Human-readable explanation."),
        ("related_item_id", "str|null", "Source item id this warning is about."),
        ("related_span_id", "str|null", "Source span id this warning is about."),
    ]
    return "\n".join(f"- {name} ({kind}): {desc}" for name, kind, desc in rows)
