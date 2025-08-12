# schemas/a3cp_core/a3cp_message.py

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class A3CPMessage(BaseModel):
    schema_version: str = Field("1.1.0", examples=["1.1.0"])
    record_id: UUID
    user_id: str
    session_id: str
    timestamp: datetime  # must be ISO 8601 with ms precision + 'Z'
    modality: Literal["gesture", "audio", "speech", "image", "multimodal"]
    source: Literal["communicator", "caregiver", "system"]

    model_config = {
        "extra": "allow",  # allow optional fields like classifier_output, context, etc.
    }
