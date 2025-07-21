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
        default_factory=dict,
        description="Contextual flags such as 'question_detected' or 'ambiguous_intent'",
    )
    context_topic_tag: Optional[str] = Field(
        None, description="Inferred topic or domain tag"
    )
    context_relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="How relevant the current input is to expected context",
    )
    timestamp: datetime = Field(..., description="ISO 8601 UTC timestamp of decision")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="Pseudonymous user identifier")
    unresolved_intents: Optional[List[str]] = Field(
        None, description="Intents unresolved or corrected in recent memory"
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


class ClarificationMetadata(BaseModel):
    needed: bool = Field(..., description="Whether clarification is required")
    reason: Optional[str] = Field(
        None, description="Trigger reason (e.g. 'low_confidence', 'tie_score')"
    )
    candidates: Optional[List[str]] = Field(
        None, description="Top ambiguous intent candidates"
    )
    confidence_scores: Optional[List[float]] = Field(
        None, description="Confidence values aligned with candidates"
    )
    threshold_used: Optional[float] = Field(
        None, description="Threshold value that triggered clarification"
    )


class ClarificationPlannerOutput(BaseModel):
    clarification: ClarificationMetadata = Field(
        ..., description="Clarification decision metadata"
    )
    decision_metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description=(
            "Explanation for clarification decision (thresholds, context flags, "
            "ambiguity reasons). Forwarded to feedback_log and memory_interface."
        ),
    )
    final_decision: Optional[str] = Field(
        None, description="Optional resolved intent if clarification is bypassed"
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "clarification": {
                "needed": True,
                "reason": "confidence_gap_below_threshold",
                "candidates": ["eat", "play"],
                "confidence_scores": [0.52, 0.48],
                "threshold_used": 0.05,
            },
            "decision_metadata": {
                "trigger_reason": "Confidence gap below 0.05",
                "thresholds": "min_confidence=0.6, min_gap=0.05",
                "context_flags": "question_detected, ambiguous_intent",
            },
            "final_decision": None,
        }
