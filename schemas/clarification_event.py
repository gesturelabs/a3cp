from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

INTERFACE_SCHEMA_PATH = "interfaces/clarification_event.schema.json"


class ClarificationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Annotated[str, Field(default="1.0.0", frozen=True)]
    record_id: Annotated[
        UUID,
        Field(description="ID of the original A3CPMessage requiring clarification"),
    ]
    user_id: Annotated[str, Field(description="Pseudonymous user ID")]
    session_id: Annotated[
        str, Field(description="Session ID associated with the interaction")
    ]
    timestamp: Annotated[
        datetime, Field(description="UTC timestamp of clarification event")
    ]

    trigger_reason: Annotated[
        str,
        Field(description="Cause of clarification: 'low_confidence', 'conflict', etc."),
    ]
    clarification_type: Annotated[
        str,
        Field(
            description="Form: 'binary', 'multiple_choice', 'reask', 'confirm_previous'"
        ),
    ]

    options_presented: Annotated[
        Optional[List[str]],
        Field(default=None, description="Candidate intents/options shown"),
    ]
    user_response: Annotated[
        Optional[str],
        Field(default=None, description="Raw or interpreted user response"),
    ]
    resolved_intent: Annotated[
        Optional[str],
        Field(default=None, description="Intent decided after clarification"),
    ]
    clarification_successful: Annotated[
        Optional[bool],
        Field(default=None, description="Whether ambiguity was resolved"),
    ]

    notes: Annotated[
        Optional[str],
        Field(default=None, description="Optional freeform diagnostic or trace info"),
    ]
