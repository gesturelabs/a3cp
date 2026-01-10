# schemas/session_manager_end/session_manager_end.py
from datetime import datetime, timezone
from typing import Optional

from pydantic import Field, field_validator

from schemas import BaseSchema


class SessionEndInput(BaseSchema):
    """
    Canonical input to end a session.
    Inherits BaseSchema; requires that session_id is present.
    """

    end_time: datetime = Field(..., description="UTC timestamp when session ended")

    # Runtime enforcement: session_id must be present on input
    @field_validator("session_id")
    @classmethod
    def _require_session_id(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("session_id is required in SessionEndInput")
        return v

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
            "session_id": "sess_1a2b3c4d5e6f7a8b",
            "timestamp": "2025-07-28T15:31:00.000Z",  # message creation timestamp
            # source is optional at input (could be UI/caregiver/system)
            "end_time": "2025-07-28T15:30:00.000Z",
        }


class SessionEndOutput(BaseSchema):
    """
    Canonical output after a session is ended.
    Inherits BaseSchema; enforces session_id presence at runtime.
    """

    end_time: datetime = Field(..., description="UTC timestamp when session ended")

    # Runtime enforcement: session_id must be present on output
    @field_validator("session_id")
    @classmethod
    def _require_session_id(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("session_id is required in SessionEndOutput")
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
            "record_id": "5b9d3aa1-1d2e-40a6-a2d9-0b5c52d0abcd",
            "user_id": "elias01",
            "session_id": "sess_1a2b3c4d5e6f7a8b",
            "timestamp": "2025-07-28T15:31:01.000Z",  # server acknowledgement time
            "source": "session_manager",
            "end_time": "2025-07-28T15:30:00.000Z",
        }
