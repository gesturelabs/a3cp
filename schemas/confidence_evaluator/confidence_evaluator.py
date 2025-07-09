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
