# apps/landmark_extractor/tests/test_ingest_boundary_validation.py

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from apps.landmark_extractor.ingest_boundary import INGEST_SINK, ingest


def test_ingest_boundary_validates_union():
    INGEST_SINK.clear()

    # ---- valid frame ----
    frame_msg = {
        "schema_version": "1.0.1",
        "record_id": str(uuid4()),
        "user_id": "u1",
        "session_id": "s1",
        "timestamp": datetime.now(timezone.utc),
        "event": "capture.frame",
        "capture_id": str(uuid4()),
        "seq": 1,
        "timestamp_frame": datetime.now(timezone.utc),
        "frame_data": "ZmFrZQ==",  # base64
    }

    asyncio.run(ingest(frame_msg))
    assert len(INGEST_SINK) == 1

    # ---- valid terminal close ----
    terminal_msg = {
        "schema_version": "1.0.1",
        "record_id": str(uuid4()),
        "user_id": "u1",
        "session_id": "s1",
        "timestamp": datetime.now(timezone.utc),
        "event": "capture.close",
        "capture_id": str(uuid4()),
        "timestamp_end": datetime.now(timezone.utc),
        "error_code": None,
    }

    asyncio.run(ingest(terminal_msg))
    assert len(INGEST_SINK) == 2

    # ---- invalid terminal (missing required error_code on abort) ----
    bad_terminal = {
        "schema_version": "1.0.1",
        "record_id": str(uuid4()),
        "user_id": "u1",
        "session_id": "s1",
        "timestamp": datetime.now(timezone.utc),
        "event": "capture.abort",
        "capture_id": str(uuid4()),
        "timestamp_end": datetime.now(timezone.utc),
        # missing error_code
    }

    with pytest.raises(ValidationError):
        asyncio.run(ingest(bad_terminal))
