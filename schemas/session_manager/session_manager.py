# session_manager Pydantic model
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContextInfo(BaseModel):
    context_partner_speech: Optional[str] = Field(
        None, description="Partner or caregiver speech that preceded the session"
    )
    session_notes: Optional[str] = Field(
        None, description="Freeform notes describing user state or session context"
    )


class SessionStartEvent(BaseModel):
    session_id: str = Field(..., description="Globally unique session identifier")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    start_time: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of session start"
    )
    modality: str = Field(
        ...,
        description="Input modality that initiated the session (e.g., gesture, speech)",
    )
    context: Optional[ContextInfo] = Field(
        None, description="Optional session context (speech prompt, caregiver notes)"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "session_id": "sess_20250714_e01",
            "user_id": "elias01",
            "start_time": "2025-07-14T17:40:00.000Z",
            "modality": "gesture",
            "context": {
                "context_partner_speech": "Do you want to play?",
                "session_notes": "User just finished snack, seemed alert",
            },
        }

    @staticmethod
    def example_output() -> dict:
        return SessionStartEvent.example_input()


class SessionEndEvent(BaseModel):
    session_id: str = Field(..., description="Session identifier to close")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    end_time: datetime = Field(
        ..., description="UTC ISO 8601 timestamp when session ended"
    )
    duration_seconds: Optional[int] = Field(
        None, description="Optional duration of session in seconds"
    )
    event_count: Optional[int] = Field(
        None, description="Optional count of logged events in this session"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "session_id": "sess_20250714_e01",
            "user_id": "elias01",
            "end_time": "2025-07-14T17:52:30.000Z",
            "duration_seconds": 750,
            "event_count": 14,
        }

    @staticmethod
    def example_output() -> dict:
        return SessionEndEvent.example_input()
