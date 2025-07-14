# output_planner Pydantic model
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


class OutputPlannerInput(BaseModel):
    output_phrase: str = Field(..., description="Phrase to deliver to AAC UI layer")
    final_decision: str = Field(..., description="Resolved intent label (e.g., 'eat')")
    output_type: Literal["intent"] = Field(..., description="Must be 'intent'")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="UTC ISO 8601 timestamp of decision")
    context: Optional[ContextInfo] = Field(
        None, description="Environmental and conversational context"
    )
    user_profile: Optional[UserProfile] = Field(
        None, description="User-specific modality and style preferences"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "output_phrase": "I want to eat",
            "final_decision": "eat",
            "output_type": "intent",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:35:00.000Z",
            "context": {
                "context_location": "kitchen",
                "context_partner_speech": "Are you hungry?",
                "context_prompt_type": "natural_use",
            },
            "user_profile": {
                "tone": "polite",
                "verbosity": "short",
                "mode_preference": "speech",
            },
        }


class OutputPlannerDecision(BaseModel):
    output_mode: Literal["speech", "text", "symbol"] = Field(
        ..., description="Selected output modality for AAC rendering"
    )
    output_phrase: str = Field(..., description="Phrase to be rendered to the user")
    final_decision: str = Field(..., description="Resolved intent that was expressed")
    output_type: Literal["intent"] = Field(..., description="Must be 'intent'")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="UTC ISO 8601 time of dispatch")
    context: Optional[ContextInfo] = Field(
        None, description="Echoed environmental context for audit trace"
    )
    user_profile: Optional[UserProfile] = Field(
        None, description="Echoed user preference profile used in output selection"
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "output_mode": "speech",
            "output_phrase": "I want to eat",
            "final_decision": "eat",
            "output_type": "intent",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:35:00.123Z",
            "context": {
                "context_location": "kitchen",
                "context_partner_speech": "Are you hungry?",
                "context_prompt_type": "natural_use",
            },
            "user_profile": {
                "tone": "polite",
                "verbosity": "short",
                "mode_preference": "speech",
            },
        }
