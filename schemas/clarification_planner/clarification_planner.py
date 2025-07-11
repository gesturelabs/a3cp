# clarification_planner Pydantic model
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RankedIntent(BaseModel):
    intent: str = Field(..., description="Predicted intent label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ClarificationPlannerInput(BaseModel):
    classifier_output: List[RankedIntent] = Field(
        ..., description="Ranked intents with confidence scores"
    )
    context_flags: Optional[Dict[str, bool]] = Field(
        default_factory=dict, description="Contextual flags (e.g., question_detected)"
    )
    context_topic_tag: Optional[str] = Field(None, description="Inferred topic tag")
    context_relevance_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Context relevance to known intents"
    )
    timestamp: datetime = Field(..., description="UTC ISO 8601 timestamp")
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    unresolved_intents: Optional[List[str]] = Field(
        None, description="Recent unresolved or corrected intents"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "classifier_output": [
                {"intent": "eat", "confidence": 0.52},
                {"intent": "play", "confidence": 0.48},
            ],
            "context_flags": {"question_detected": True, "ambiguous_intent": True},
            "context_topic_tag": "food",
            "context_relevance_score": 0.87,
            "timestamp": "2025-07-09T09:32:45.123Z",
            "session_id": "a3cp_sess_2025-07-09_elias01",
            "user_id": "elias01",
            "unresolved_intents": ["drink", "rest"],
        }


class ClarificationPlannerOutput(BaseModel):
    clarification_trigger: bool = Field(
        ..., description="Whether clarification should be requested"
    )
    clarification_payload: Optional[Dict] = Field(
        None, description="Payload passed to LLM Clarifier"
    )
    audit_log: Dict[str, str] = Field(
        ..., description="Explanation and threshold criteria for decision"
    )
    final_decision_override: Optional[str] = Field(
        None,
        description="Optional final decision suggestion if clarification is skipped",
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "clarification_trigger": True,
            "clarification_payload": {
                "top_candidates": ["eat", "play"],
                "confidence_gap": 0.04,
                "ambiguous_reason": "tie_score_below_threshold",
            },
            "audit_log": {
                "trigger_reason": "Confidence gap below threshold (0.05)",
                "thresholds": "min_confidence=0.6, min_gap=0.05",
                "detected_flags": "question_detected, ambiguous_intent",
            },
            "final_decision_override": None,
        }
