from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from schemas.base.base_schema import BaseSchema


class SessionStartRequest(BaseModel):
    """
    Canonical input schema from UI or other sources to start a session.
    """

    user_id: str = Field(..., description="Pseudonymous user identifier")
    is_training_data: Optional[bool] = Field(
        default=False,
        description="Flag indicating if this session is for labeled training data",
    )
    session_notes: Optional[str] = Field(
        default=None,
        description="Optional free-text notes or context about the session",
    )
    performer_id: Optional[str] = Field(
        default=None,
        description="Identifier for the actual input actor if different from user_id",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "is_training_data": True,
            "session_notes": "Training session with carer miming gestures",
            "performer_id": "carer01",
        }


class SessionStartResponse(BaseSchema):
    """
    Canonical output schema returned to UI or caller after session creation.
    Inherits common metadata from BaseSchema.
    """

    start_time: datetime = Field(..., description="UTC timestamp when session started")
    is_training_data: bool = Field(..., description="Flag indicating training session")
    session_notes: Optional[str] = Field(
        default=None, description="Echoed notes or context about the session"
    )
    # performer_id, modality, source inherited optionally from BaseSchema

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "a8c43e6e-4f1d-4b2f-b8ee-123456789abc",
            "user_id": "elias01",
            "session_id": "sess_20250728_001",
            "timestamp": "2025-07-28T14:00:00.000Z",
            "source": "session_manager",
            "performer_id": "carer01",
            "start_time": "2025-07-28T14:00:00.000Z",
            "is_training_data": True,
            "session_notes": "Training session with carer miming gestures",
        }
