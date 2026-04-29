"""Source span schema for Case Structurer.

SourceSpan represents a quoted span from one RawTextInput.

It is used for provenance inside a single free-text input. It tells the
system where a structured field came from in the original user-provided
text.

This schema must not represent uploaded documents, files, clinical
sections, evidence atoms, diagnoses, hypotheses, conflicts, or actions.
"""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common import InputID, SpanID


def _new_span_id() -> SpanID:
    """Generate a stable source span id."""
    return f"span_{uuid4().hex}"


class SourceSpan(BaseModel):
    """A quoted text span from one RawTextInput.

    SourceSpan is a provenance object. It answers one question:

        Where in the original input text did this structured information
        come from?

    It does not interpret the clinical meaning of the text.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    span_id: SpanID = Field(
        default_factory=_new_span_id,
        description="Unique id for this source span.",
    )

    input_id: InputID = Field(
        ...,
        description="Id of the RawTextInput that contains this quoted span.",
    )

    quoted_text: str = Field(
        ...,
        min_length=1,
        description="Exact or near-exact text fragment quoted from the raw input.",
    )

    char_start: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Optional zero-based inclusive character start index in the raw text. "
            "Use None when reliable character-level alignment is unavailable."
        ),
    )

    char_end: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Optional zero-based exclusive character end index in the raw text. "
            "Use None when reliable character-level alignment is unavailable."
        ),
    )

    @field_validator("quoted_text")
    @classmethod
    def quoted_text_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only quoted text."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("quoted_text must not be empty.")
        return cleaned

    @model_validator(mode="after")
    def validate_char_offsets(self) -> "SourceSpan":
        """Validate optional character offsets.

        char_start and char_end are optional because LLM-generated character
        offsets may be unreliable in copied clinical text.

        If one offset is provided, both must be provided.
        If both are provided, char_end must be greater than char_start.
        """
        start = self.char_start
        end = self.char_end

        if (start is None) != (end is None):
            raise ValueError(
                "char_start and char_end must either both be provided or both be None."
            )

        if start is not None and end is not None and end <= start:
            raise ValueError("char_end must be greater than char_start.")

        return self