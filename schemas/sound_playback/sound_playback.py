# sound_playback Pydantic model
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AudioPlaybackRequest(BaseModel):
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Associated session identifier")
    timestamp: datetime = Field(..., description="Timestamp of original audio capture")
    file_uri: str = Field(..., description="Path or URI to the audio file (e.g., .wav)")
    consent_given: Optional[bool] = Field(
        None,
        description="Whether the user has consented to this recording being played",
    )
    is_demo: Optional[bool] = Field(
        None, description="Whether this is a demo/test file, not real data"
    )
    intent_label: Optional[str] = Field(
        None, description="Intent label associated with the recording, if available"
    )
    label_status: Optional[Literal["unconfirmed", "confirmed", "corrected"]] = Field(
        None, description="Label trust status at review time"
    )
    annotation_context: Optional[str] = Field(
        None, description="Freeform notes, e.g., reason for review or clarification tag"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:50:00.000Z",
            "file_uri": "./data/audio/elias01_20250714_175000.wav",
            "consent_given": True,
            "is_demo": False,
            "intent_label": "play",
            "label_status": "confirmed",
            "annotation_context": "Caregiver unclear if user meant 'play' or 'music'",
        }

    @staticmethod
    def example_output() -> dict:
        return AudioPlaybackRequest.example_input()
