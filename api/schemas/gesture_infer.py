# api/schemas/gesture_infer.py

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel


class IntentCandidate(BaseModel):
    label: str
    confidence: float


class A3CPMessage(BaseModel):
    classifier_output: List[IntentCandidate]
    record_id: str
    user_id: str
    session_id: str
    timestamp: datetime
    modality: Literal["gesture"]
    source: str
    vector: str  # This is a reference ID, not raw data

    model_config = {
        "json_schema_extra": {
            "example": {
                "classifier_output": [
                    {"label": "want-drink", "confidence": 0.92},
                    {"label": "need-help", "confidence": 0.07},
                ],
                "record_id": "rec-12345",
                "user_id": "user-abc",
                "session_id": "sess-789",
                "timestamp": "2025-06-12T12:34:56.789Z",
                "modality": "gesture",
                "source": "simulator",
                "vector": "vector-uuid-001",
            }
        }
    }
