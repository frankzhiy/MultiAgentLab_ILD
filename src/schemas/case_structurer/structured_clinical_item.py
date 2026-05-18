"""Structured clinical item schema for the Case Structurer.

StructuredClinicalItem represents a source-level clinical statement extracted
from one ClinicalSection.

It answers one question:

    What source-level clinical statement appears inside this section?

StructuredClinicalItem is still part of case structuring. It must not
represent tree-shaped evidence, parsed attributes, diagnoses, hypotheses, conflicts,
actions, treatment recommendations, or arbitration results.

Evidence-level tree structuring belongs to the Evidence Tree Structurer, and
attribute role labeling belongs to the evidence-tree stage when needed.
"""

from __future__ import annotations

from enum import StrEnum

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
from src.utils.id_generator import generate_item_id

from .common import (
    CertaintyLevel,
    ConfidenceLevel,
    InputID,
    ItemID,
    NegationStatus,
    SectionID,
    TemporalRelation,
)
from .source_span import SourceSpan


class ClinicalItemType(StrEnum):
    """Fine-grained clinical item type.

    This is more specific than ClinicalSectionType.

    ClinicalSectionType answers:
        What broad clinical block does this text belong to?

    ClinicalItemType answers:
        What specific kind of clinical fact is this item?

    This enum must not include diagnostic hypothesis categories such as
    IPF, CTD-ILD, fibrotic HP, infection, or acute exacerbation. Those
    belong to later hypothesis-level schemas, not Case Structurer schemas.
    """

    DEMOGRAPHIC = "demographic"

    SYMPTOM = "symptom"
    SIGN = "sign"

    DIAGNOSIS_HISTORY = "diagnosis_history"
    COMORBIDITY = "comorbidity"

    LAB_RESULT = "lab_result"
    IMAGING_FINDING = "imaging_finding"
    PATHOLOGY_FINDING = "pathology_finding"
    PULMONARY_FUNCTION = "pulmonary_function"

    MEDICATION = "medication"
    PROCEDURE = "procedure"

    EXPOSURE = "exposure"
    SMOKING_HISTORY = "smoking_history"
    FAMILY_HISTORY = "family_history"
    ALLERGY = "allergy"

    TREATMENT = "treatment"
    TREATMENT_RESPONSE = "treatment_response"
    FOLLOW_UP_FINDING = "follow_up_finding"

    MDT_STATEMENT = "mdt_statement"

    UNCERTAIN = "uncertain"


class StructuredClinicalItem(BaseModel):
    """A source-level clinical statement extracted from one ClinicalSection.

    StructuredClinicalItem turns section-level text into stable source-level
    clinical statements. It does not parse values, units, time expressions, or
    body sites, and it does not split coordinated source statements into
    minimal evidence tree nodes.

    It does not answer:

    - What diagnosis is likely?
    - What hypothesis does this item support or refute?
    - What evidence tree node should be created?
    - What attribute spans should be role-labeled?
    - What treatment should be recommended?
    - What conflict exists?
    - What action should be taken?

    Those responsibilities belong to later schemas and agents.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: ItemID = Field(
        default_factory=generate_item_id,
        description="Unique id for this structured clinical item.",
    )

    input_id: InputID = Field(
        ...,
        description="RawTextInput id that this clinical item was extracted from.",
    )

    section_id: SectionID = Field(
        ...,
        description=(
            "ClinicalSection id that this item belongs to. "
            "The item references the section by id to avoid deep nested imports."
        ),
    )

    item_type: ClinicalItemType = Field(
        ...,
        description=(
            "Fine-grained clinical item type, such as symptom, lab_result, "
            "imaging_finding, medication, exposure, or treatment_response."
        ),
    )

    temporality: TemporalRelation = Field(
        default=TemporalRelation.UNKNOWN,
        description=(
            "Broad temporal status of this clinical item, such as current, "
            "past, chronic, recent_worsening, follow_up, or unknown."
        ),
    )

    certainty: CertaintyLevel = Field(
        default=CertaintyLevel.UNKNOWN,
        description=(
            "Certainty of this clinical statement as expressed in the source "
            "text, not diagnostic certainty."
        ),
    )

    negation: NegationStatus = Field(
        default=NegationStatus.UNKNOWN,
        description=(
            "Whether this clinical item is present, absent, denied, not "
            "mentioned, or unknown."
        ),
    )

    source_spans: list[SourceSpan] = Field(
        ...,
        min_length=1,
        description=(
            "Source spans showing where this clinical item came from in the "
            "original RawTextInput. At least one span is required for provenance."
        ),
    )

    item_order: int = Field(
        ...,
        ge=1,
        description=(
            "Order of this item within the same RawTextInput. This is text "
            "order, not necessarily clinical event time."
        ),
    )

    classification_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Confidence in item_type and item boundary classification. "
            "This is extraction confidence, not diagnostic confidence."
        ),
    )

    notes: str | None = Field(
        default=None,
        description=(
            "Optional non-diagnostic note about item extraction or classification. "
            "Must not include diagnosis, hypothesis, evidence polarity, treatment "
            "recommendation, conflict, action, or arbitration result."
        ),
    )

    @field_validator(
        "notes",
        mode="after",
    )
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        """Normalize optional text fields.

        Blank strings are converted to None to avoid meaningless metadata.
        """
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        return cleaned

    @model_validator(mode="before")
    @classmethod
    def _drop_legacy_derived_keys(cls, data: Any) -> Any:
        """Silently drop legacy stored fields that are now computed.

        ``label`` used to be an LLM-authored free-text field. It is now a
        computed property derived from ``source_spans``. To remain backward
        compatible with historical JSON payloads and tolerant of LLM output
        that still emits the key, we strip it before validation.
        """
        if isinstance(data, dict) and "label" in data:
            data = dict(data)
            data.pop("label", None)
        return data

    @computed_field  # type: ignore[prop-decorator]
    @property
    def label(self) -> str:
        """Concatenation of ``source_spans[*].quoted_text`` in document order.

        ``label`` is intentionally derived from the item's source spans rather
        than authored by the LLM. This guarantees the item label is exactly
        what is grounded in raw_text, with no paraphrasing or information
        loss when downstream stages consume the canonical statement.
        """
        ordered = sorted(
            self.source_spans,
            key=lambda span: (
                span.char_start if span.char_start is not None else float("inf")
            ),
        )
        parts = [
            span.quoted_text.strip()
            for span in ordered
            if span.quoted_text and span.quoted_text.strip()
        ]
        return " ".join(parts)

    @model_validator(mode="after")
    def validate_source_span_input_consistency(self) -> "StructuredClinicalItem":
        """Validate that all source spans come from the same RawTextInput.

        A StructuredClinicalItem belongs to one RawTextInput. Therefore,
        every SourceSpan attached to this item must have the same input_id.
        """
        mismatched_span_ids = [
            span.span_id
            for span in self.source_spans
            if span.input_id != self.input_id
        ]

        if mismatched_span_ids:
            raise ValueError(
                "All source_spans must have the same input_id as the "
                f"StructuredClinicalItem. Mismatched span ids: {mismatched_span_ids}"
            )

        return self
