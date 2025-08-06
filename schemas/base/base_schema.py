from datetime import datetime
from typing import Annotated, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    schema_version: Annotated[
        str,
        Field(..., description="Semantic version of the schema (MAJOR.MINOR.PATCH)"),
    ]
    record_id: Annotated[
        UUID,
        Field(..., description="Unique ID for this message (UUIDv4)"),
    ]
    user_id: Annotated[
        str,
        Field(..., description="Pseudonymous user identifier"),
    ]
    session_id: Optional[
        Annotated[
            str,
            Field(
                description="Session ID grouping related inputs; assigned by session_manager"
            ),
        ]
    ] = None
    timestamp: Annotated[
        datetime,
        Field(
            ...,
            description="UTC ISO 8601 timestamp with milliseconds and 'Z' suffix",
        ),
    ]
    modality: Optional[
        Annotated[
            Literal["gesture", "audio", "speech", "image", "multimodal"],
            Field(description="Modality of input or message"),
        ]
    ] = None
    source: Optional[
        Annotated[
            str,
            Field(
                description="Originating module or component name (e.g., 'gesture_classifier', 'session_manager')"
            ),
        ]
    ] = None
    performer_id: Optional[
        Annotated[
            str,
            Field(
                description=(
                    "Person performing input; required for human-originated data, "
                    "may differ from user_id; use 'system' for system-generated inputs"
                )
            ),
        ]
    ] = None

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
            "user_id": "elias01",
            "timestamp": "2025-06-15T12:34:56.789Z",
            "performer_id": "carer01",
            # Optional fields omitted for brevity
        }

    @staticmethod
    def example_output() -> dict:
        return BaseSchema.example_input()
