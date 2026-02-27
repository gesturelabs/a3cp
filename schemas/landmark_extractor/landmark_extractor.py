# schemas/landmark_extractor.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Dict, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from schemas import BaseSchema

LandmarkExtractorEventIn = Literal["capture.frame", "capture.close", "capture.abort"]


class LandmarkExtractorFrameInput(BaseSchema):
    event: Annotated[
        Literal["capture.frame"],
        Field(description="Per-frame ingest event (image payload included)"),
    ] = "capture.frame"

    # FIX: provide defaults when overriding BaseSchema fields
    modality: Annotated[
        Literal["image"],
        Field(description="Sensor modality (aligned with capture stream)"),
    ] = "image"

    source: Annotated[
        Literal["camera_feed_worker"],
        Field(description="Upstream source module"),
    ] = "camera_feed_worker"

    capture_id: Annotated[
        str, Field(..., description="Stable capture identifier (same for all frames)")
    ]
    seq: Annotated[
        int, Field(..., ge=1, description="Frame sequence number (starts at 1)")
    ]
    timestamp_frame: Annotated[
        datetime,
        Field(..., description="Event-time timestamp for the frame (UTC)"),
    ]

    frame_data: Annotated[
        str,
        Field(
            ...,
            description=(
                "Base64-encoded image (typically JPEG). May be a data URL "
                "(data:image/jpeg;base64,...) or raw base64."
            ),
        ),
    ]

    frame_id: Optional[str] = Field(
        None,
        description="Optional frame identifier (legacy). Prefer deriving from (capture_id, seq).",
    )

    @field_validator("timestamp_frame", mode="before")
    @classmethod
    def _coerce_timestamp_frame_utc(cls, v):
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("timestamp_frame must be ISO 8601 string or datetime")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt

    @field_validator("frame_data")
    @classmethod
    def _frame_data_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("frame_data must be a non-empty string")
        return v


class LandmarkExtractorTerminalInput(BaseSchema):
    event: Annotated[
        Literal["capture.close", "capture.abort"],
        Field(..., description="Terminal event for this capture"),
    ]

    # FIX: provide defaults when overriding BaseSchema fields
    modality: Annotated[
        Literal["image"],
        Field(description="Sensor modality (aligned with capture stream)"),
    ] = "image"

    source: Annotated[
        Literal["camera_feed_worker"],
        Field(description="Upstream source module"),
    ] = "camera_feed_worker"

    capture_id: Annotated[
        str, Field(..., description="Stable capture identifier to finalize")
    ]
    timestamp_end: Annotated[
        datetime,
        Field(..., description="Event-time timestamp for capture end (UTC)"),
    ]

    error_code: Optional[str] = Field(
        None,
        description="Required if event == capture.abort. Must be None if event == capture.close.",
    )

    @field_validator("timestamp_end", mode="before")
    @classmethod
    def _coerce_timestamp_end_utc(cls, v):
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("timestamp_end must be ISO 8601 string or datetime")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt

    @model_validator(mode="after")
    def _validate_error_code(self) -> "LandmarkExtractorTerminalInput":
        if self.event == "capture.abort":
            if not self.error_code or not str(self.error_code).strip():
                raise ValueError("error_code is required when event == 'capture.abort'")
        if self.event == "capture.close":
            if self.error_code is not None:
                raise ValueError(
                    "error_code must be None when event == 'capture.close'"
                )
        return self


LandmarkExtractorIngest = Annotated[
    Union[LandmarkExtractorFrameInput, LandmarkExtractorTerminalInput],
    Field(discriminator="event"),
]


# Demo-only payloads (unchanged)
class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float
    visibility: float


class LandmarkVector(BaseModel):
    pose_landmarks: Dict[str, LandmarkPoint] = Field(default_factory=dict)
    left_hand_landmarks: Dict[str, LandmarkPoint] = Field(default_factory=dict)
    right_hand_landmarks: Dict[str, LandmarkPoint] = Field(default_factory=dict)
    face_landmarks: Dict[str, LandmarkPoint] = Field(default_factory=dict)


class LandmarkExtractorOverlayOutput(BaseModel):
    capture_id: str
    seq: int
    timestamp_frame: str
    landmarks: LandmarkVector
