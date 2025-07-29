# schemas/session_manager/session_manager.py
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class SessionStartRequest(BaseModel):
    """
    Main input schema for the session_manager module.
    Also defines the module-wide example_input / example_output pair.
    """

    user_id: str = Field(..., description="Pseudonymous user identifier")

    is_training_data: bool = Field(
        default=False,
        description="True if session is for labeled training data collection",
    )

    modality: Optional[List[Literal["gesture", "speech", "sound", "typing"]]] = Field(
        default=None, description="Only required if is_training_data is true"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_modality_if_training(cls, data):
        if data.get("is_training_data") and not data.get("modality"):
            raise ValueError("modality is required when is_training_data is true")
        return data

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "is_training_data": True,
            "modality": ["gesture", "sound"],
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "session_id": "sess_20250728_001",
            "user_id": "elias01",
            "start_time": "2025-07-28T14:00:00Z",
            "is_training_data": True,
            "modality": ["gesture", "sound"],
        }


class SessionStartResponse(BaseModel):
    session_id: str = Field(..., description="System-generated session identifier")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    start_time: datetime = Field(..., description="UTC timestamp when session started")
    is_training_data: bool = Field(
        ..., description="Whether session was for training data"
    )
    modality: Optional[List[Literal["gesture", "speech", "sound", "typing"]]] = Field(
        default=None, description="Included only if is_training_data is true"
    )


class SessionEndEvent(BaseModel):
    session_id: str = Field(..., description="Session identifier to close")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    end_time: datetime = Field(..., description="UTC timestamp when session ended")
    duration_seconds: Optional[int] = Field(
        None, description="Optional duration of session in seconds"
    )
    event_count: Optional[int] = Field(
        None, description="Optional number of events recorded in session"
    )
