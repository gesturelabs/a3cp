# confidence_evaluator Pydantic model
# confidence_evaluator.py

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RankedIntent(BaseModel):
    intent: str = Field(..., description="Predicted intent label")
    base_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Raw classifier confidence"
    )
    memory_boost: Optional[float] = Field(
        0.0, description="Score adjustment based on memory"
    )
    context_alignment: Optional[float] = Field(
        0.0, description="Score adjustment from context relevance"
    )
    final_score: Optional[float] = Field(
        None, description="Computed total score (used post-processing only)"
    )


class ConfidenceEvaluatorInput(BaseModel):
    classifier_output: List[RankedIntent] = Field(
        ..., description="Intent candidates with base scores"
    )
    memory_intent_boosts: Optional[Dict[str, float]] = Field(
        default_factory=dict, description="User memory-derived intent weights"
    )
    context_topic_tag: Optional[str] = Field(None, description="Current topic tag")
    context_relevance_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Contextual match score"
    )
    timestamp: datetime = Field(..., description="ISO timestamp of decision")
    session_id: str = Field(..., description="Session ID for traceability")
    user_id: str = Field(..., description="User identifier")

    @staticmethod
    def example_input() -> dict:
        return {
            "classifier_output": [
                {
                    "intent": "eat",
                    "base_confidence": 0.62,
                    "memory_boost": 0.15,
                    "context_alignment": 0.10,
                },
                {
                    "intent": "play",
                    "base_confidence": 0.60,
                    "memory_boost": 0.05,
                    "context_alignment": 0.02,
                },
            ],
            "memory_intent_boosts": {"eat": 0.15, "play": 0.05},
            "context_topic_tag": "food",
            "context_relevance_score": 0.92,
            "timestamp": "2025-07-09T09:45:12.789Z",
            "session_id": "a3cp_sess_2025-07-09_elias01",
            "user_id": "elias01",
        }


class ConfidenceEvaluatorOutput(BaseModel):
    classifier_output: List[RankedIntent] = Field(
        ..., description="Ranked intent candidates with computed scores"
    )
    context_flags: Optional[Dict[str, bool]] = Field(
        default_factory=dict, description="Optional decision flags"
    )
    final_decision: Optional[str] = Field(
        None, description="Final chosen intent if confidence is decisive"
    )
    timestamp: datetime = Field(..., description="UTC timestamp of output")
    audit_log: Dict[str, str] = Field(..., description="Scoring breakdown for auditing")

    @staticmethod
    def example_output() -> dict:
        return {
            "classifier_output": [
                {
                    "intent": "eat",
                    "base_confidence": 0.62,
                    "memory_boost": 0.15,
                    "context_alignment": 0.10,
                    "final_score": 0.87,
                },
                {
                    "intent": "play",
                    "base_confidence": 0.60,
                    "memory_boost": 0.05,
                    "context_alignment": 0.02,
                    "final_score": 0.67,
                },
            ],
            "context_flags": {"high_confidence": True, "tie_score": False},
            "final_decision": "eat",
            "timestamp": "2025-07-09T09:45:12.902Z",
            "audit_log": {
                "scoring_method": "weighted_sum(v1)",
                "threshold_applied": "final_score > 0.85",
                "decision_rationale": "eat scored significantly above others",
            },
        }
