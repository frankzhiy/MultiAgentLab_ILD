from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.evidence_atomizer.atomization_warning import AtomizationWarning


class CoverageUnit(BaseModel):
    """Internal pre-atomization unit that defines required evidence coverage."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    unit_id: str
    source_item_id: str
    source_attribute_ids: list[str] = Field(default_factory=list)
    source_span_ids: list[str]
    surface_text: str
    clinical_object: str
    status_or_direction: str | None
    modifier_texts: list[str] = Field(default_factory=list)
    assertion_status: str
    certainty: str
    temporality: str
    split_basis: str
    required: bool = True
    assertion_cue_text: str | None = None
    assertion_scope_text: str | None = None
    clinical_object_type: str | None = None
    clinical_object_assertion_id: str | None = None
    source_frame_node_ids: list[str] = Field(default_factory=list)
    context_frame_node_ids: list[str] = Field(default_factory=list)
    parent_frame_node_id: str | None = None
    relation_to_parent: str | None = None
    inherited_context_text: str | None = None
    local_content_text: str | None = None
    atomization_policy: str | None = None


class CoverageUnitBuildResult(BaseModel):
    """Internal result of deterministic coverage-unit construction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    coverage_units: list[CoverageUnit] = Field(default_factory=list)
    warnings: list[AtomizationWarning | str] = Field(default_factory=list)
