from __future__ import annotations

from .assertion_aware_coverage_unit_builder import AssertionAwareCoverageUnitBuilder


class CoverageUnitBuilder(AssertionAwareCoverageUnitBuilder):
    """Backward-compatible alias for the assertion-aware coverage unit builder."""


__all__ = ["CoverageUnitBuilder"]
