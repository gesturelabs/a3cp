# output_expander Pydantic model
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ContextInfo(BaseModel):
    context_location: Optional[str] = Field(
        None, description="Coarse location or room tag (e.g., 'kitchen')"
    )
    context_partner_speech: Optional[str] = Field(
        None,
        description="What the communication partner said (verbatim or paraphrased)",
    )
    context_prompt_type: Optional[str] = Field(
        None, description="Prompt category, e.g., 'natural_use', 'prompted', 'other'"
    )


class UserProfile(BaseModel):
    tone: Optional[str] = Field(
        None,
        description="Preferred communicative tone, e.g., 'polite', 'direct', 'playful'",
    )
    verbosity: Optional[str] = Field(
        None, description="Preferred verbosity level, e.g., 'short', 'verbose'"
    )
    mode_preference: Optional[str] = Field(
        None, description="Preferred output modality, e.g., 'speech', 'text', 'symbol'"
    )


class OutputExpansionInput(BaseModel):
    final_decision: str = Field(
        ..., description="Intent to be rendered (e.g., 'drink')"
    )
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="UTC ISO 8601 timestamp of request")
    output_type: Literal["intent"] = Field(..., description="Must be 'intent'")
    context: Optional[ContextInfo] = Field(
        None, description="Environmental and conversational context"
    )
    user_profile: Optional[UserProfile] = Field(
        None, description="User-specific style and phrasing preferences"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "final_decision": "drink",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:30:00.000Z",
            "output_type": "intent",
            "context": {
                "context_location": "kitchen",
                "context_partner_speech": "Are you thirsty?",
            },
            "user_profile": {
                "tone": "polite",
                "verbosity": "short",
                "mode_preference": "speech",
            },
        }


class OutputExpansionResult(BaseModel):
    output_phrase: str = Field(..., description="Generated phrase to render or speak")
    output_mode: Literal["speech", "text", "symbol"] = Field(
        ..., description="Delivery channel for AAC output"
    )
    final_decision: str = Field(
        ..., description="Original intent label that was expanded"
    )
    user_id: str = Field(..., description="Pseudonymous user ID")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 time of phrase generation"
    )
    output_type: Literal["intent"] = Field(..., description="Type of resolved output")
    context: Optional[ContextInfo] = Field(
        None, description="Environmental and conversational context (echoed)"
    )
    user_profile: Optional[UserProfile] = Field(
        None, description="User-specific tone and phrasing profile (echoed)"
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "output_phrase": "Can I have a drink?",
            "output_mode": "speech",
            "final_decision": "drink",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:32:00.000Z",
            "output_type": "intent",
            "context": {
                "context_location": "kitchen",
                "context_partner_speech": "Are you thirsty?",
            },
            "user_profile": {
                "tone": "polite",
                "verbosity": "short",
                "mode_preference": "speech",
            },
        }
