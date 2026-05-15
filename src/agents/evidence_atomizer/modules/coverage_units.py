from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CoverageUnit(BaseModel):
    """Internal pre-atomization unit that defines required evidence coverage."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    unit_id: str
    source_item_id: str
    source_span_ids: list[str]
    surface_text: str
    clinical_object: str
    status_or_direction: str | None
    value: str | None
    unit: str | None
    body_site: str | None
    assertion_status: str
    certainty: str
    temporality: str
    time_text: str | None
    split_basis: str
    required: bool = True


class CoverageUnitBuildResult(BaseModel):
    """Internal result of deterministic coverage-unit construction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    coverage_units: list[CoverageUnit] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
