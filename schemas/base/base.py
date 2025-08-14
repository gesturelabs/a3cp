# schema/base/base_schema.py
import re
from datetime import datetime, timezone
from typing import Annotated, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class BaseSchema(BaseModel):
    schema_version: Annotated[
        str, Field(..., description="Semantic version (MAJOR.MINOR.PATCH)")
    ]
    record_id: Annotated[
        UUID, Field(..., description="Unique ID for this message (UUIDv4)")
    ]
    user_id: Annotated[str, Field(..., description="Pseudonymous user identifier")]
    session_id: Optional[
        Annotated[str, Field(description="Session ID from session_manager")]
    ] = None
    timestamp: Annotated[
        datetime,
        Field(..., description="UTC ISO 8601 with milliseconds and 'Z' suffix"),
    ]
    modality: Optional[
        Annotated[
            Literal["gesture", "audio", "speech", "image", "multimodal"],
            Field(description="Input/message modality"),
        ]
    ] = None
    source: Optional[
        Annotated[
            str, Field(description="Originating component (e.g., 'gesture_classifier')")
        ]
    ] = None
    performer_id: Optional[
        Annotated[
            str,
            Field(description="Actor producing input; 'system' for system-generated"),
        ]
    ] = None

    # --- Validation hardening ---
    @field_validator("schema_version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not SEMVER_RE.match(v):
            raise ValueError("schema_version must be MAJOR.MINOR.PATCH (e.g., '1.0.1')")
        return v

    @field_validator("timestamp", mode="before")
    @classmethod
    def _coerce_utc(cls, v):
        """Accepts str or datetime; returns timezone-aware UTC datetime."""
        if isinstance(v, str):
            # Let Pydantic parse; we enforce tz below
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("timestamp must be ISO 8601 string or datetime")
        if dt.tzinfo is None:
            # Assume provided time is UTC if naive; make explicit
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt


# --- Single source of truth for examples (module-level) ---
def example_input() -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "timestamp": "2025-06-15T12:34:56.789Z",
        "performer_id": "carer01",
        # Optional fields intentionally omitted
    }


def example_output() -> dict:
    # Base is symmetric: output example equals input example
    return example_input()
