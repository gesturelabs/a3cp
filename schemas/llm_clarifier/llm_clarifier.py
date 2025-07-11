# llm_clarifier Pydantic model
# schemas/llm_clarifier.py

"""
Schema for the `llm_clarifier` module.

This module generates clarification prompts using a local LLM
based on ambiguous or low-confidence classifier outputs.
It returns a prompt to be shown to the user and logs input/output
for future retraining and audit.
"""

from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field


class IntentCandidate(BaseModel):
    label: str = Field(..., description="Intent label (e.g., 'eat', 'play')")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0–1.0)"
    )


class LLMClarifierInput(BaseModel):
    session_id: Annotated[str, Field(..., description="Session identifier")]
    user_id: Annotated[str, Field(..., description="User pseudonym or identifier")]
    timestamp: Annotated[str, Field(..., description="UTC ISO 8601 timestamp")]
    topic_tag: Optional[str] = Field(
        None, description="Thematic topic tag (e.g., 'meal', 'help')"
    )
    flags: List[str] = Field(
        ..., description="List of clarification flags (e.g., 'low_confidence')"
    )
    intent_candidates: List[IntentCandidate] = Field(
        ..., description="Ranked list of intent candidates with scores"
    )


class LLMClarifierOutput(BaseModel):
    output_phrase: str = Field(
        ..., description="Clarification prompt to be shown to user"
    )
    output_mode: Literal["multiple_choice", "open_ended", "yes_no"] = Field(
        ..., description="Type of clarification prompt"
    )
    updated_flags: List[str] = Field(
        ..., description="Flags to carry forward or revise"
    )
    logging_summary: dict = Field(
        ..., description="Compact summary of input + generated prompt for logging"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "session_id": "sess_20250711_e01",
            "user_id": "elias01",
            "timestamp": "2025-07-11T15:45:10.000Z",
            "topic_tag": "meal",
            "flags": ["low_confidence", "ambiguous_gesture"],
            "intent_candidates": [
                {"label": "eat", "confidence": 0.42},
                {"label": "help", "confidence": 0.40},
                {"label": "play", "confidence": 0.18},
            ],
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "output_phrase": "Did you mean eat, help, or play?",
            "output_mode": "multiple_choice",
            "updated_flags": ["clarification_prompt_issued"],
            "logging_summary": {
                "top_candidates": ["eat", "help", "play"],
                "prompt": "Did you mean eat, help, or play?",
                "origin_flags": ["low_confidence", "ambiguous_gesture"],
                "topic": "meal",
            },
        }
