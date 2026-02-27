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
