"""Attribute modification scope for target-grounded ClinicalAttribute objects."""

from __future__ import annotations

from enum import StrEnum


class AttributeScope(StrEnum):
    """Scope of the source-copied phrase modified by a ClinicalAttribute."""

    ITEM = "item"
    LOCAL_PHRASE = "local_phrase"
    COORDINATED_OBJECTS = "coordinated_objects"
    UNCERTAIN = "uncertain"
