"""Prompt rendering utilities for the Case Structurer."""

from .output_skeletons import (
    clinical_section_skeleton,
    stage_context_skeleton,
    structured_item_skeleton,
)
from .prompt_context import (
    format_available_items,
    format_available_sections,
    format_forbidden_objects,
    format_raw_input_summary,
    format_source_span_policy,
    format_stage_context_summary,
)
from .schema_contracts import (
    clinical_section_contract,
    enum_values,
    format_enum_values,
    stage_context_contract,
    structured_item_contract,
)
from .template_renderer import PromptTemplateRenderer

__all__ = [
    "PromptTemplateRenderer",
    "clinical_section_contract",
    "clinical_section_skeleton",
    "enum_values",
    "format_available_items",
    "format_available_sections",
    "format_enum_values",
    "format_forbidden_objects",
    "format_raw_input_summary",
    "format_source_span_policy",
    "format_stage_context_summary",
    "stage_context_contract",
    "stage_context_skeleton",
    "structured_item_contract",
    "structured_item_skeleton",
]
