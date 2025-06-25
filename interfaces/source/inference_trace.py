from datetime import datetime
from typing import Annotated, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

INTERFACE_SCHEMA_PATH = "interfaces/inference_trace.schema.json"


class InferenceTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Annotated[str, Field(default="1.0.0", frozen=True)]
    record_id: Annotated[UUID, Field(description="ID of the A3CPMessage being traced")]
    session_id: Annotated[
        str, Field(description="Session ID tied to the original input")
    ]
    timestamp: Annotated[
        datetime, Field(description="UTC timestamp of inference event")
    ]

    module_name: Annotated[
        str,
        Field(
            description="Name of module performing inference, e.g., 'gesture_classifier'"
        ),
    ]
    model_version: Annotated[
        str, Field(description="Version of model used in inference")
    ]
    predicted_intent: Annotated[str, Field(description="Top predicted intent")]
    intent_confidence: Annotated[
        float, Field(description="Confidence score of top intent prediction")
    ]

    candidate_intents: Annotated[
        Optional[Dict[str, float]],
        Field(default=None, description="Full intent ranking with confidence scores"),
    ]
    memory_hint_used: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="Whether memory-based intent boosts influenced result",
        ),
    ]
    fallback_triggered: Annotated[
        Optional[bool],
        Field(default=None, description="Whether fallback mechanism was used"),
    ]
    memory_fallback_suggestions: Annotated[
        Optional[List[str]],
        Field(
            default=None,
            description="Suggested fallback intents if primary prediction was uncertain",
        ),
    ]
    decision_reasoning: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Explanation or rule trace used to finalize decision",
        ),
    ]
    downstream_decision: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Final decision passed to downstream module, if different from predicted_intent",
        ),
    ]
