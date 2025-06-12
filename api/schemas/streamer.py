# api/schemas/streamer.py

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Literal, Optional, List
from datetime import datetime


class RawInput(BaseModel):
    user_id: str
    session_id: str
    timestamp: datetime
    modality: Literal["gesture", "sound"]
    source: str  # e.g., "webcam", "mic", "simulator"
    intent_label: str
    consent_given: bool
    raw_input_audio: Optional[List[float]] = None
    raw_input_video: Optional[List[float]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "u-1234",
                "session_id": "s-5678",
                "timestamp": "2025-06-12T12:34:56.789Z",
                "modality": "gesture",
                "source": "webcam",
                "intent_label": "want-drink",
                "consent_given": True,
                "raw_input_video": [0.1, 0.2, 0.3, 0.4]
            }
        }
    )
