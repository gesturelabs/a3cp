# schemas/session_manager/session_manager_start/session_manager_start.py

from datetime import datetime, timezone
from typing import Optional

from pydantic import Field, field_validator

from schemas import BaseSchema


class SessionStartInput(BaseSchema):
    """
    Canonical input schema from UI or other sources to start a session.
    Extends BaseSchema for versioning, record_id, user_id, timestamp, etc.
    """

    is_training_data: Optional[bool] = Field(
        default=False,
        description="True if session is intended for labeled training data",
    )
    session_notes: Optional[str] = Field(
        default=None,
        description="Optional free-text notes or context about the session",
    )
    performer_id: Optional[str] = Field(
        default=None,
        description=(
            "Identifier for the actor initiating the session. "
            "If omitted, it may be interpreted downstream as equivalent to user_id; "
            "the session manager does not auto-fill this field."
        ),
    )

    training_intent_label: Optional[str] = Field(
        default=None,
        description="Intent label or meaning of the gesture if this is a training session",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
            "user_id": "elias01",
            "timestamp": "2025-07-28T14:00:00.000Z",
            "is_training_data": True,
            "session_notes": "Training session with carer miming gestures",
            "performer_id": "carer01",
            "training_intent_label": "help",
        }


class SessionStartOutput(BaseSchema):
    """
    Canonical output schema returned after session creation.
    Inherits common metadata from BaseSchema and enforces that
    session_id is always present in valid outputs.
    """

    # Override BaseSchema's Optional session_id to make it required + non-null here
    session_id: str = Field(default=..., description="Session ID from session_manager")  # type: ignore[assignment]

    start_time: datetime = Field(..., description="UTC timestamp when session started")
    is_training_data: bool = Field(..., description="Flag indicating training session")
    session_notes: Optional[str] = Field(
        default=None, description="Echoed notes or context about the session"
    )
    training_intent_label: Optional[str] = Field(
        default=None, description="Echoed intent label if this is a training session"
    )

    # Runtime enforcement: session_id must not be None
    @field_validator("session_id")
    @classmethod
    def _require_session_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("session_id is required in SessionStartOutput")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "a8c43e6e-4f1d-4b2f-b8ee-123456789abc",
            "user_id": "elias01",
            "session_id": "sess_1a2b3c4d5e6f7a8b",
            "timestamp": "2025-07-28T14:00:00.000Z",
            "source": "session_manager",
            "performer_id": "carer01",
            "start_time": "2025-07-28T14:00:00.000Z",
            "is_training_data": True,
            "session_notes": "Training session with carer miming gestures",
            "training_intent_label": "help",
        }
