# feedback_log Pydantic model
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FeedbackLogEntry(BaseModel):
    entry_id: UUID = Field(
        default_factory=uuid4, description="Unique ID for this clarification event"
    )
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of caregiver feedback"
    )
    session_id: str = Field(..., description="Session identifier for grouping")
    user_id: str = Field(..., description="Pseudonymous or actual user identifier")

    prompt_text: str = Field(
        ..., description="Clarification prompt shown to the caregiver or partner"
    )
    user_response: str = Field(
        ..., description="Verbatim or normalized user/caregiver reply"
    )

    intent_label: str = Field(..., description="Original intent label under review")
    label_correction: Optional[str] = Field(
        None, description="Corrected intent label, if caregiver provided one"
    )
    label_status: Literal["confirmed", "corrected", "rejected"] = Field(
        ..., description="Label trust status: confirmed, corrected, or rejected"
    )

    output_mode: Optional[str] = Field(
        None,
        description="Mode of AAC or system output at time of prompt (e.g., 'speech', 'symbol')",
    )
