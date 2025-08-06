from datetime import datetime, timezone

from pydantic import Field

from schemas.base.base_schema import BaseSchema


class SessionEndEvent(BaseSchema):
    """
    Canonical input/output schema for ending a session.
    """

    end_time: datetime = Field(..., description="UTC timestamp when session ended")
    # Optional fields can be added here if needed, e.g., performer_id, session_notes

    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "f17e3c34-8f23-4f9a-bb89-123456789abc",
            "user_id": "elias01",
            "session_id": "sess_20250728_001",
            "timestamp": "2025-07-28T15:31:00.000Z",  # message creation timestamp
            "source": "session_manager",
            "end_time": "2025-07-28T15:30:00.000Z",
        }

    @staticmethod
    def example_output() -> dict:
        return SessionEndEvent.example_input()
