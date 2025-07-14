# memory_interface Pydantic model
# schemas/memory_interface/memory_interface.py

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryAuditEntry(BaseModel):
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Session identifier for grouping")
    timestamp: datetime = Field(..., description="UTC ISO 8601 timestamp of event")
    intent_label: str = Field(..., description="Intent attempted by user")
    label_status: str = Field(
        ...,
        description='Label status outcome: one of "confirmed", "corrected", or "rejected"',
    )
    final_decision: Optional[str] = Field(
        None,
        description="Final intent label after clarification or override (if available)",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T10:32:45.678Z",
            "intent_label": "eat",
            "label_status": "confirmed",
            "final_decision": "eat",
        }


class MemoryFields(BaseModel):
    intent_boosts: Dict[str, float] = Field(
        ..., description="Per-intent confidence modifiers derived from memory traces"
    )
    fallback_suggestions: Optional[List[str]] = Field(
        default=None,
        description="Ranked fallback intents in case of low classifier confidence",
    )
    hint_used: Optional[bool] = Field(
        default=None,
        description="Whether memory hints were used in current decision context",
    )


class MemoryQueryResult(BaseModel):
    memory: MemoryFields = Field(
        ..., description="Memory-derived hints for intent boosting and fallback support"
    )
    final_decision: Optional[str] = Field(
        None,
        description="Final decision (if available), logged for downstream alignment",
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "memory": {
                "intent_boosts": {"eat": 0.12, "play": 0.04},
                "fallback_suggestions": ["rest", "drink"],
                "hint_used": True,
            },
            "final_decision": "eat",
        }
