# speech_transcriber Pydantic model
from typing import Optional

from pydantic import BaseModel, Field


class SpeechTranscriptSegment(BaseModel):
    transcript: str = Field(
        ..., description="Transcribed speech segment (finalized or partial)"
    )
    timestamp: str = Field(
        ..., description="UTC ISO8601 time of capture or segment end"
    )
    session_id: str = Field(..., description="Interaction session identifier")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Optional ASR confidence score (0.0–1.0)"
    )
    language: Optional[str] = Field(
        None, description="Language code (e.g., 'en', 'es') in BCP-47 format"
    )
    segment_id: Optional[str] = Field(
        None, description="Optional unique ID for this ASR segment"
    )
    is_partial: Optional[bool] = Field(
        False,
        description="True if this is a live/partial transcript; False if finalized",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "transcript": "Do you want to play?",
            "timestamp": "2025-07-14T17:58:00.000Z",
            "session_id": "sess_20250714_e01",
            "user_id": "elias01",
            "confidence": 0.94,
            "language": "en",
            "segment_id": "asr_00023",
            "is_partial": False,
        }

    @staticmethod
    def example_output() -> dict:
        return SpeechTranscriptSegment.example_input()
