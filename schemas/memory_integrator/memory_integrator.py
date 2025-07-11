# memory_integrator Pydantic model
# schemas/memory_integrator.py

"""
Schema for the `memory_integrator` module.

This module adjusts classifier intent rankings based on per-user memory traces.
It applies recency, frequency, and correction-based boosts, and logs the influence
of memory on final decision making.
"""

from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IntentCandidate(BaseModel):
    label: str = Field(..., description="Intent label (e.g., 'eat', 'play')")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model-assigned base confidence score"
    )


class AdjustedIntentCandidate(BaseModel):
    label: str = Field(..., description="Intent label after memory adjustment")
    base_score: float = Field(
        ..., ge=0.0, le=1.0, description="Original classifier confidence"
    )
    adjusted_score: float = Field(
        ...,
        ge=0.0,
        le=1.5,
        description="Adjusted confidence after applying memory boosts",
    )


class MemoryIntegratorInput(BaseModel):
    session_id: Annotated[str, Field(..., description="Session identifier")]
    user_id: Annotated[str, Field(..., description="User pseudonym or identifier")]
    timestamp: Annotated[str, Field(..., description="ISO 8601 UTC timestamp")]
    classifier_output: List[IntentCandidate] = Field(
        ..., description="Classifier outputs before memory adjustment"
    )
    intent_boosts: Dict[str, float] = Field(
        ...,
        description="Memory-derived per-intent boost values (e.g., from recency/frequency/corrections)",
    )
    hint_used: List[str] = Field(
        ..., description="List of memory signals used (e.g., 'recency', 'frequency')"
    )


class MemoryIntegratorOutput(BaseModel):
    adjusted_output: List[AdjustedIntentCandidate] = Field(
        ...,
        description="Re-ranked or re-scored classifier outputs after memory influence",
    )
    hint_used: List[str] = Field(
        ..., description="Memory hints actually applied during adjustment"
    )
    final_decision: Optional[str] = Field(
        None, description="Optional top-ranked intent after memory adjustment"
    )
    logging_summary: Dict[str, Any] = Field(
        ..., description="Trace of input vs adjusted scores and memory features used"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "session_id": "sess_20250711_e01",
            "user_id": "elias01",
            "timestamp": "2025-07-11T16:05:00.000Z",
            "classifier_output": [
                {"label": "eat", "confidence": 0.42},
                {"label": "help", "confidence": 0.38},
                {"label": "play", "confidence": 0.20},
            ],
            "intent_boosts": {"eat": 0.10, "help": 0.05},
            "hint_used": ["recency", "correction_boost"],
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "adjusted_output": [
                {"label": "eat", "base_score": 0.42, "adjusted_score": 0.52},
                {"label": "help", "base_score": 0.38, "adjusted_score": 0.43},
                {"label": "play", "base_score": 0.20, "adjusted_score": 0.20},
            ],
            "hint_used": ["recency", "correction_boost"],
            "final_decision": "eat",
            "logging_summary": {
                "applied_boosts": {"eat": 0.10, "help": 0.05},
                "original_order": ["eat", "help", "play"],
                "adjusted_order": ["eat", "help", "play"],
                "selected": "eat",
            },
        }
