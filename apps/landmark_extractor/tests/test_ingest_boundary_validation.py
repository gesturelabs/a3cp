# apps/landmark_extractor/tests/test_ingest_boundary_validation.py

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from apps.landmark_extractor import service
from apps.landmark_extractor.ingest_boundary import ingest


def test_ingest_boundary_validates_union(monkeypatch):
    captured = {"messages": []}

    async def fake_handle_message(message):
        captured["messages"].append(message)

    monkeypatch.setattr(service, "handle_message", fake_handle_message)

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
        "frame_data": "ZmFrZQ==",
    }

    asyncio.run(ingest(frame_msg))
    assert len(captured["messages"]) == 1
    assert captured["messages"][0].event == "capture.frame"

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
    assert len(captured["messages"]) == 2
    assert captured["messages"][1].event == "capture.close"

    bad_terminal = {
        "schema_version": "1.0.1",
        "record_id": str(uuid4()),
        "user_id": "u1",
        "session_id": "s1",
        "timestamp": datetime.now(timezone.utc),
        "event": "capture.abort",
        "capture_id": str(uuid4()),
        "timestamp_end": datetime.now(timezone.utc),
    }

    with pytest.raises(ValidationError):
        asyncio.run(ingest(bad_terminal))
