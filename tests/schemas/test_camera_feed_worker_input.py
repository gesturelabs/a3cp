# tests/schemas/test_camera_feed_worker_input.py

import pytest
from pydantic import ValidationError

from schemas import CameraFeedWorkerInput


def test_annotation_rejected_when_not_capture_open():
    payload = {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "session_id": "sess_1a2b3c4d5e6f7a8b",
        "timestamp": "2025-07-28T15:31:00.000Z",
        "modality": "image",
        "source": "ui",
        "event": "capture.frame_meta",  # NOT capture.open
        "capture_id": "cap_9f7c2a",
        "seq": 1,
        "timestamp_frame": "2025-07-28T15:31:00.000Z",
        "byte_length": 1234,
        "annotation": {"intent": "wave"},  # Should be rejected
    }

    with pytest.raises(ValidationError):
        CameraFeedWorkerInput(**payload)


def test_annotation_validator_triggers_based_on_event():
    """
    Proves `event` is available at validation time:
    - Same payload is valid for capture.open (with annotation + required open fields)
    - Same payload shape is invalid if only `event` changes to capture.frame_meta,
      even when frame_meta required fields are present.
    """

    # A) Valid: capture.open may include annotation
    open_payload = {
        "schema_version": "1.0.1",
        "record_id": "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56",
        "user_id": "elias01",
        "session_id": "sess_1a2b3c4d5e6f7a8b",
        "timestamp": "2025-07-28T15:31:00.000Z",
        "modality": "image",
        "source": "ui",
        "event": "capture.open",
        "capture_id": "cap_9f7c2a",
        "timestamp_start": "2025-07-28T15:31:00.000Z",
        "fps_target": 15,
        "width": 640,
        "height": 480,
        "encoding": "jpeg",
        "annotation": {"intent": "wave"},
    }

    m_open = CameraFeedWorkerInput(**open_payload)
    assert m_open.event == "capture.open"
    assert m_open.annotation is not None
    assert m_open.annotation.intent == "wave"

    # B) Invalid: change ONLY event (keep annotation), and provide required fields for frame_meta
    frame_meta_payload = dict(open_payload)
    frame_meta_payload["event"] = "capture.frame_meta"

    # Remove open-only requirements and add frame_meta requirements to avoid "missing fields" noise
    frame_meta_payload.pop("timestamp_start", None)
    frame_meta_payload.pop("fps_target", None)
    frame_meta_payload.pop("width", None)
    frame_meta_payload.pop("height", None)
    frame_meta_payload.pop("encoding", None)

    frame_meta_payload["seq"] = 1
    frame_meta_payload["timestamp_frame"] = "2025-07-28T15:31:00.000Z"
    frame_meta_payload["byte_length"] = 1234

    with pytest.raises(ValidationError) as e:
        CameraFeedWorkerInput(**frame_meta_payload)

    # Ensure the specific constraint is what fired
    assert "annotation is only allowed on capture.open" in str(e.value)
