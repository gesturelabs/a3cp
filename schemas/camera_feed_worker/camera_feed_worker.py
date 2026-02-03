# schemas/camera_feed_worker/camera_feed_worker.py
#
# Sprint 1 (browser → server) control-plane schemas only.
# Binary JPEG bytes are NOT part of any schema; they travel as WS binary frames.
#
# Timestamp semantics:
# - BaseSchema.timestamp      = message creation / ingest timestamp (control-plane)
# - timestamp_start/frame/end = event-time timestamps (data-plane)

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

from pydantic import Field, field_validator, model_validator

from schemas import BaseSchema

# ---------------------------------------------------------------------------
# Input (client → camera_feed_worker): unified superset input schema
# ---------------------------------------------------------------------------

CameraFeedWorkerEventIn = Literal[
    "capture.open",
    "capture.frame_meta",
    "capture.close",
]


class CameraFeedWorkerInput(BaseSchema):
    """
    Canonical JSON control-message input for camera_feed_worker.

    Notes:
    - This schema models ONLY JSON control messages.
    - Frame bytes are transported separately as WS binary frames and are not modeled here.
    """

    event: Annotated[
        CameraFeedWorkerEventIn,
        Field(..., description="Control message type for the capture protocol"),
    ]

    # Correlation (required for all events)
    capture_id: Annotated[
        str, Field(..., description="Stable capture ID for the entire capture")
    ]

    # --- Open-only fields ---
    timestamp_start: Optional[
        Annotated[datetime, Field(description="Event-time start of capture (UTC)")]
    ] = None
    fps_target: Optional[Annotated[int, Field(description="Target FPS requested")]] = (
        None
    )
    width: Optional[Annotated[int, Field(description="Frame width in pixels")]] = None
    height: Optional[Annotated[int, Field(description="Frame height in pixels")]] = None
    encoding: Optional[
        Annotated[str, Field(description="Frame encoding (e.g., 'jpeg')")]
    ] = None

    # --- Frame-meta-only fields ---
    seq: Optional[
        Annotated[int, Field(description="Frame sequence number, starts at 1")]
    ] = None
    timestamp_frame: Optional[
        Annotated[
            datetime, Field(description="Event-time timestamp of the frame (UTC)")
        ]
    ] = None
    byte_length: Optional[
        Annotated[
            int, Field(description="Declared byte length of the next binary frame")
        ]
    ] = None

    # --- Close-only fields ---
    timestamp_end: Optional[
        Annotated[datetime, Field(description="Event-time end of capture (UTC)")]
    ] = None

    # Event-time coercion (mirrors BaseSchema.timestamp coercion behavior)
    @field_validator(
        "timestamp_start", "timestamp_frame", "timestamp_end", mode="before"
    )
    @classmethod
    def _coerce_event_time_utc(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError(
                "event-time timestamps must be ISO 8601 string or datetime"
            )
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt

    @model_validator(mode="after")
    def _validate_required_fields_by_event(self):
        # Keep validation structural only; protocol/limits live in service.py.
        if self.event == "capture.open":
            missing = [
                f
                for f in (
                    "timestamp_start",
                    "fps_target",
                    "width",
                    "height",
                    "encoding",
                )
                if getattr(self, f) is None
            ]
            if missing:
                raise ValueError(f"capture.open requires fields: {', '.join(missing)}")
            return self

        if self.event == "capture.frame_meta":
            missing = [
                f
                for f in ("seq", "timestamp_frame", "byte_length")
                if getattr(self, f) is None
            ]
            if missing:
                raise ValueError(
                    f"capture.frame_meta requires fields: {', '.join(missing)}"
                )
            return self

        if self.event == "capture.close":
            if self.timestamp_end is None:
                raise ValueError("capture.close requires field: timestamp_end")
            return self

        raise ValueError("invalid event value")


# ---------------------------------------------------------------------------
# Output (camera_feed_worker → client): minimal Sprint 1 control output
# ---------------------------------------------------------------------------

CameraFeedWorkerEventOut = Literal["capture.abort"]


class CameraFeedWorkerOutput(BaseSchema):
    """
    Canonical JSON control-message output for camera_feed_worker (Sprint 1 minimal).

    Only abort messages are defined at schema level.
    Success-path behavior is transport-defined (e.g., close without error) and/or
    expressed via service actions, not via JSON output schemas.
    """

    event: Annotated[
        CameraFeedWorkerEventOut,
        Field(..., description="Control message type emitted by camera_feed_worker"),
    ]

    capture_id: Annotated[
        str, Field(..., description="Capture ID associated with this response")
    ]

    error_code: Annotated[
        str, Field(..., description="Stable error_code for abort events")
    ]


# ---------------------------------------------------------------------------
# Examples (module-level; exactly one input + one output example)
# ---------------------------------------------------------------------------


def example_input() -> dict:
    # Example: capture.open
    return {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "session_id": "sess_1a2b3c4d5e6f7a8b",
        "timestamp": "2025-07-28T15:31:00.000Z",  # message timestamp
        "modality": "image",
        "source": "ui",
        "event": "capture.open",
        "capture_id": "cap_9f7c2a",
        "timestamp_start": "2025-07-28T15:31:00.000Z",  # event-time
        "fps_target": 15,
        "width": 640,
        "height": 480,
        "encoding": "jpeg",
    }


def example_output() -> dict:
    # Example: capture.abort
    return {
        "schema_version": "1.0.1",
        "record_id": "5b9d3aa1-1d2e-40a6-a2d9-0b5c52d0abcd",
        "user_id": "elias01",
        "session_id": "sess_1a2b3c4d5e6f7a8b",
        "timestamp": "2025-07-28T15:31:01.000Z",  # server emit time
        "modality": "image",
        "source": "camera_feed_worker",
        "event": "capture.abort",
        "capture_id": "cap_9f7c2a",
        "error_code": "protocol_violation",
    }
