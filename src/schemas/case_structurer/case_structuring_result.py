"""Final output schema for the Case Structurer.

CaseStructuringResult is the only formal output of the Case Structurer.

It assembles:
- RawTextInput
- StageContext
- ClinicalSection objects
- StructuredClinicalItem objects
- TimelineEvent objects
- AmbiguityItem objects

into one validated case-structuring package.

This schema performs cross-object consistency checks, such as:
- all objects belong to the same RawTextInput;
- stage context and raw input refer to the same case;
- StructuredClinicalItem.section_id references existing ClinicalSection ids;
- TimelineEvent.related_item_ids reference existing StructuredClinicalItem ids;
- AmbiguityItem related ids reference existing section/item ids;
- duplicate ids and duplicate ordering are detected.

This schema must not contain:
- EvidenceAtom
- HypothesisState
- Conflict
- ActionPlan
- UpdateTrace
- ArbitrationResult
- SafetyGateResult
- diagnosis or treatment recommendation fields
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .ambiguity_item import AmbiguityItem
from .clinical_section import ClinicalSection
from .common import ValidationSeverity
from .raw_text_input import RawTextInput
from .stage_context import StageContext
from .structured_clinical_item import StructuredClinicalItem
from .timeline_event import TimelineEvent


class StructuringWarning(BaseModel):
    """Warning or error produced during case structuring.

    This is a lightweight validation message attached to CaseStructuringResult.
    It is not a diagnostic warning, safety gate result, conflict object, or
    downstream reasoning artifact.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    severity: ValidationSeverity = Field(
        ...,
        description="Severity of this structuring message.",
    )

    code: str = Field(
        ...,
        min_length=1,
        description=(
            "Stable machine-readable warning code, such as "
            "'missing_sections', 'low_stage_confidence', or "
            "'mostly_ambiguous_input'."
        ),
    )

    message: str = Field(
        ...,
        min_length=1,
        description=(
            "Human-readable explanation of the structuring issue. "
            "Must not contain diagnosis, hypothesis, evidence polarity, "
            "treatment recommendation, conflict resolution, or action advice."
        ),
    )

    related_object_id: str | None = Field(
        default=None,
        description=(
            "Optional id of the related object, such as section_id, item_id, "
            "event_id, ambiguity_id, span_id, input_id, or stage_id."
        ),
    )

    @field_validator("code", "message", mode="after")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only required text fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Required text fields must not be empty.")
        return cleaned

    @field_validator("related_object_id", mode="after")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        return cleaned


class CaseStructuringResult(BaseModel):
    """Validated output package of the Case Structurer.

    CaseStructuringResult answers one question:

        What structured case representation was produced from this one
        RawTextInput?

    It does not answer:

    - What diagnosis is likely?
    - What hypothesis does an item support or refute?
    - What evidence atom should be used for reasoning?
    - What conflict exists between hypotheses?
    - What treatment should be recommended?
    - What action should be taken?
    - What final arbitration result should be produced?

    Those responsibilities belong to later schemas, agents, and phases.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    input: RawTextInput = Field(
        ...,
        description="Raw free-text input that this structuring result is based on.",
    )

    stage_context: StageContext = Field(
        ...,
        description=(
            "Workflow context describing where this input fits in the case "
            "trajectory."
        ),
    )

    clinical_sections: list[ClinicalSection] = Field(
        default_factory=list,
        description=(
            "Coarse clinical sections extracted from the raw input. "
            "These are section-level groupings, not evidence atoms."
        ),
    )

    structured_items: list[StructuredClinicalItem] = Field(
        default_factory=list,
        description=(
            "Fine-grained clinical items extracted from clinical sections. "
            "These are still case-structuring objects, not reasoning evidence."
        ),
    )

    timeline_events: list[TimelineEvent] = Field(
        default_factory=list,
        description=(
            "Time-related clinical events extracted from the raw input. "
            "These describe chronology, not diagnostic interpretation."
        ),
    )

    ambiguities: list[AmbiguityItem] = Field(
        default_factory=list,
        description=(
            "Ambiguous, uncertain, conflicting, or under-specified statements "
            "that should not be forced into definite structured interpretations."
        ),
    )

    structuring_warnings: list[StructuringWarning] = Field(
        default_factory=list,
        description=(
            "Warnings or errors produced during structuring. "
            "These are about extraction and validation quality, not diagnosis."
        ),
    )

    ready_for_evidence_atomization: bool = Field(
        default=True,
        description=(
            "Whether this structuring result is considered ready for the "
            "Evidence Atomizer. This is not the same as Pydantic validity. "
            "A result may be schema-valid but not ready for downstream evidence "
            "atomization if it is too ambiguous or too incomplete."
        ),
    )

    @model_validator(mode="after")
    def validate_stage_matches_input(self) -> "CaseStructuringResult":
        """Validate that StageContext matches RawTextInput."""
        if self.stage_context.input_id != self.input.input_id:
            raise ValueError(
                "stage_context.input_id must match input.input_id. "
                f"Got stage_context.input_id={self.stage_context.input_id!r}, "
                f"input.input_id={self.input.input_id!r}."
            )

        if self.stage_context.case_id != self.input.case_id:
            raise ValueError(
                "stage_context.case_id must match input.case_id. "
                f"Got stage_context.case_id={self.stage_context.case_id!r}, "
                f"input.case_id={self.input.case_id!r}."
            )

        return self

    @model_validator(mode="after")
    def validate_all_objects_use_same_input(self) -> "CaseStructuringResult":
        """Validate that all child objects belong to the same RawTextInput."""
        expected_input_id = self.input.input_id

        mismatched_sections = [
            section.section_id
            for section in self.clinical_sections
            if section.input_id != expected_input_id
        ]

        mismatched_items = [
            item.item_id
            for item in self.structured_items
            if item.input_id != expected_input_id
        ]

        mismatched_events = [
            event.event_id
            for event in self.timeline_events
            if event.input_id != expected_input_id
        ]

        mismatched_ambiguities = [
            ambiguity.ambiguity_id
            for ambiguity in self.ambiguities
            if ambiguity.input_id != expected_input_id
        ]

        errors: list[str] = []

        if mismatched_sections:
            errors.append(f"clinical_sections={mismatched_sections}")

        if mismatched_items:
            errors.append(f"structured_items={mismatched_items}")

        if mismatched_events:
            errors.append(f"timeline_events={mismatched_events}")

        if mismatched_ambiguities:
            errors.append(f"ambiguities={mismatched_ambiguities}")

        if errors:
            raise ValueError(
                "All child objects must have the same input_id as RawTextInput. "
                "Mismatched objects: " + "; ".join(errors)
            )

        return self

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "CaseStructuringResult":
        """Validate that ids are unique within each object category."""
        self._raise_if_duplicate(
            values=[section.section_id for section in self.clinical_sections],
            label="clinical_sections.section_id",
        )

        self._raise_if_duplicate(
            values=[item.item_id for item in self.structured_items],
            label="structured_items.item_id",
        )

        self._raise_if_duplicate(
            values=[event.event_id for event in self.timeline_events],
            label="timeline_events.event_id",
        )

        self._raise_if_duplicate(
            values=[ambiguity.ambiguity_id for ambiguity in self.ambiguities],
            label="ambiguities.ambiguity_id",
        )

        return self

    @model_validator(mode="after")
    def validate_section_references(self) -> "CaseStructuringResult":
        """Validate references from StructuredClinicalItem to ClinicalSection."""
        section_ids = {section.section_id for section in self.clinical_sections}

        missing_section_refs = [
            {
                "item_id": item.item_id,
                "missing_section_id": item.section_id,
            }
            for item in self.structured_items
            if item.section_id not in section_ids
        ]

        if missing_section_refs:
            raise ValueError(
                "Every StructuredClinicalItem.section_id must reference an "
                f"existing ClinicalSection.section_id. Missing refs: {missing_section_refs}"
            )

        return self

    @model_validator(mode="after")
    def validate_timeline_item_references(self) -> "CaseStructuringResult":
        """Validate references from TimelineEvent to StructuredClinicalItem."""
        item_ids = {item.item_id for item in self.structured_items}

        missing_item_refs: list[dict[str, str]] = []

        for event in self.timeline_events:
            for related_item_id in event.related_item_ids:
                if related_item_id not in item_ids:
                    missing_item_refs.append(
                        {
                            "event_id": event.event_id,
                            "missing_item_id": related_item_id,
                        }
                    )

        if missing_item_refs:
            raise ValueError(
                "Every TimelineEvent.related_item_ids entry must reference an "
                f"existing StructuredClinicalItem.item_id. Missing refs: {missing_item_refs}"
            )

        return self

    @model_validator(mode="after")
    def validate_ambiguity_references(self) -> "CaseStructuringResult":
        """Validate references from AmbiguityItem to sections and items."""
        section_ids = {section.section_id for section in self.clinical_sections}
        item_ids = {item.item_id for item in self.structured_items}

        missing_section_refs: list[dict[str, str]] = []
        missing_item_refs: list[dict[str, str]] = []

        for ambiguity in self.ambiguities:
            for related_section_id in ambiguity.related_section_ids:
                if related_section_id not in section_ids:
                    missing_section_refs.append(
                        {
                            "ambiguity_id": ambiguity.ambiguity_id,
                            "missing_section_id": related_section_id,
                        }
                    )

            for related_item_id in ambiguity.related_item_ids:
                if related_item_id not in item_ids:
                    missing_item_refs.append(
                        {
                            "ambiguity_id": ambiguity.ambiguity_id,
                            "missing_item_id": related_item_id,
                        }
                    )

        errors: list[str] = []

        if missing_section_refs:
            errors.append(f"missing related_section_ids={missing_section_refs}")

        if missing_item_refs:
            errors.append(f"missing related_item_ids={missing_item_refs}")

        if errors:
            raise ValueError(
                "AmbiguityItem related ids must reference existing objects. "
                + "; ".join(errors)
            )

        return self

    @model_validator(mode="after")
    def validate_no_duplicate_order_values(self) -> "CaseStructuringResult":
        """Validate that order fields do not duplicate within each category.

        Orders do not need to be strictly continuous because extraction may
        omit unclear or irrelevant spans. However, duplicate order values make
        downstream sorting ambiguous and should be rejected.
        """
        self._raise_if_duplicate(
            values=[section.section_order for section in self.clinical_sections],
            label="clinical_sections.section_order",
        )

        self._raise_if_duplicate(
            values=[item.item_order for item in self.structured_items],
            label="structured_items.item_order",
        )

        self._raise_if_duplicate(
            values=[event.event_order for event in self.timeline_events],
            label="timeline_events.event_order",
        )

        return self

    @model_validator(mode="after")
    def validate_result_not_empty(self) -> "CaseStructuringResult":
        """Validate that the structuring result contains at least one output.

        A CaseStructuringResult may contain only ambiguities if the input is too
        unclear to structure safely. However, it should not contain no sections,
        no items, no timeline events, and no ambiguities at the same time.
        """
        has_any_structured_output = any(
            [
                self.clinical_sections,
                self.structured_items,
                self.timeline_events,
                self.ambiguities,
            ]
        )

        if not has_any_structured_output:
            raise ValueError(
                "CaseStructuringResult must contain at least one clinical section, "
                "structured item, timeline event, or ambiguity item."
            )

        return self

    @model_validator(mode="after")
    def validate_readiness_has_warning_when_false(self) -> "CaseStructuringResult":
        """Require an explanation when the result is not ready downstream."""
        if self.ready_for_evidence_atomization:
            return self

        has_warning_or_error = any(
            warning.severity in {
                ValidationSeverity.WARNING,
                ValidationSeverity.ERROR,
            }
            for warning in self.structuring_warnings
        )

        if not has_warning_or_error:
            raise ValueError(
                "ready_for_evidence_atomization=False requires at least one "
                "structuring warning with severity warning or error."
            )

        return self

    @staticmethod
    def _raise_if_duplicate(values: list[object], label: str) -> None:
        """Raise a ValueError if duplicate values are found."""
        seen: set[object] = set()
        duplicates: list[object] = []

        for value in values:
            if value in seen and value not in duplicates:
                duplicates.append(value)
            seen.add(value)

        if duplicates:
            raise ValueError(f"Duplicate values found in {label}: {duplicates}")