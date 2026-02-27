# schemas/a3cp_message/a3cp_message.py

from typing import Annotated, Dict, Optional
from uuid import UUID

from pydantic import Field, field_validator

from schemas.base.base import BaseSchema


class Annotation(BaseSchema):
    """Capture-time human annotation (fallible, training-oriented)."""

    intent: Annotated[
        str,
        Field(description="Human-provided intent label at capture.open"),
    ]


class A3CPMessage(BaseSchema):
    """
    Canonical runtime message schema for A3CP internal communication + session JSONL logging.

    Inherits the Session Spine from BaseSchema:
      schema_version, record_id, user_id, session_id?, timestamp, modality?, source?, performer_id?

    This schema deliberately allows additional optional fields via model_config.extra="allow"
    to support incremental rollout of classifier/memory/clarification/AAC fields without
    breaking older producers/consumers.
    """

    # Correlator for bounded capture windows (many frames) across modules.
    # Not part of the universal spine because not every event belongs to a capture.
    capture_id: Optional[
        Annotated[
            UUID,
            Field(description="Bounded capture/window correlator (one per capture)"),
        ]
    ] = None

    # Capture-time human annotation (dataset label; only valid on capture.open)
    annotation: Optional[Annotation] = None

    classifier_output: Optional[Dict[str, Annotated[float, Field(ge=0.0, le=1.0)]]] = (
        None
    )

    model_config = {
        "extra": "allow",
    }

    @field_validator("classifier_output")
    @classmethod
    def _require_unknown_key(cls, v):
        if v is None:
            return v
        if "unknown" not in v:
            raise ValueError('classifier_output must include key "unknown"')
        return v

    @field_validator("annotation")
    @classmethod
    def _annotation_only_on_capture_open(cls, v, info):
        if v is None:
            return v

        event = info.data.get("event")
        if event != "capture.open":
            raise ValueError("annotation is only allowed on capture.open events")

        return v

    @staticmethod
    def example_input() -> dict:
        return example_input()

    @staticmethod
    def example_output() -> dict:
        return example_output()


# --- Single source of truth for examples (module-level) ---
def example_input() -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "session_id": "sess_2025-06-15_elias01",
        "timestamp": "2025-06-15T12:34:56.789Z",
        "modality": "gesture",
        "source": "camera_feed_worker",  # emitting module name (string)
        "performer_id": "carer01",  # actor; "system" for system-generated
        "capture_id": "11111111-2222-3333-4444-555555555555",
        "annotation": {"intent": "hungry"},
        # optional extra fields allowed, e.g.:
        # "raw_features_ref": {...},
        # "classifier_output": {...},
        # "context_location": "kitchen",
    }


def example_output() -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "session_id": "sess_2025-06-15_elias01",
        "timestamp": "2025-06-15T12:34:56.789Z",
        "modality": "gesture",
        "source": "gesture_classifier",
        "performer_id": "system",
        "capture_id": "11111111-2222-3333-4444-555555555555",
        "classifier_output": {"go_outside": 0.84, "hungry": 0.12, "unknown": 0.04},
    }
