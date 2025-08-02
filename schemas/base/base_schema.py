# schemas/base/base_schema.py

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    schema_version: Annotated[
        str,
        Field(..., description="Semantic version of the schema (MAJOR.MINOR.PATCH)"),
    ]
    record_id: Annotated[
        UUID, Field(..., description="Unique ID for this message (UUIDv4)")
    ]
    user_id: Annotated[str, Field(..., description="Pseudonymous user identifier")]
    session_id: Annotated[
        str, Field(..., description="Session ID grouping related inputs")
    ]
    timestamp: Annotated[
        datetime,
        Field(
            ..., description="UTC ISO 8601 timestamp with milliseconds and 'Z' suffix"
        ),
    ]
    modality: Annotated[
        Literal["gesture", "audio", "speech", "image", "multimodal"],
        Field(..., description="Modality of input or message"),
    ]
    source: Annotated[
        Literal["communicator", "caregiver", "system"],
        Field(..., description="Source of message (e.g. who triggered it)"),
    ]

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
            "user_id": "elias01",
            "session_id": "a3cp_sess_2025-06-15_elias01",
            "timestamp": "2025-06-15T12:34:56.789Z",
            "modality": "gesture",
            "source": "communicator",
        }

    @staticmethod
    def example_output() -> dict:
        return BaseSchema.example_input()
