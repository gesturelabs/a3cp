from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class IntentCandidate(BaseModel):
    label: str
    confidence: float

class A3CPMessage(BaseModel):
    classifier_output: List[IntentCandidate]
    record_id: str
    user_id: str
    session_id: str
    timestamp: datetime
    modality: Literal["sound"]
    source: str
    vector: str  # Reference to feature vector or audio clip UUID

    model_config = {
        "json_schema_extra": {
            "example": {
                "classifier_output": [
                    {"label": "need-help", "confidence": 0.87},
                    {"label": "pain", "confidence": 0.11},
                    {"label": "bored", "confidence": 0.02}
                ],
                "record_id": "rec-audio-001",
                "user_id": "user-xyz",
                "session_id": "sess-123",
                "timestamp": "2025-06-12T12:34:56.789Z",
                "modality": "sound",
                "source": "microphone",
                "vector": "vector-uuid-001"
            }
        }
    }
