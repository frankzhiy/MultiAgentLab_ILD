"""Audit events for writes into shared case state."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.utils.id_generator import generate_id


def _utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def generate_write_event_id() -> str:
    """Generate a persistent write event id."""
    return generate_id("write_event")


class WriteStatus(StrEnum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_WARNINGS = "accepted_with_warnings"
    REJECTED = "rejected"


class WriteEvent(BaseModel):
    """Audit metadata for one state write attempt."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    event_id: str = Field(default_factory=generate_write_event_id)
    case_id: str
    writer_name: str
    agent_name: str
    object_type: str
    object_id: str | None = None
    status: WriteStatus
    message: str
    created_at: datetime = Field(default_factory=_utc_now)
