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
