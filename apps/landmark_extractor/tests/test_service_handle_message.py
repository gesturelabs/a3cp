# apps/landmark_extractor/tests/test_service_handle_message.py

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from schemas import LandmarkExtractorFrameInput, LandmarkExtractorTerminalInput


def test_handle_message_routes_capture_frame_to_handle_frame(monkeypatch):
    called = {"value": False}

    def fake_handle_frame(message: LandmarkExtractorFrameInput) -> None:
        called["value"] = True

    monkeypatch.setattr(service, "_handle_frame", fake_handle_frame)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=uuid4(),
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    asyncio.run(service.handle_message(message))

    assert called["value"] is True


def test_handle_message_routes_capture_close_to_handle_close(monkeypatch):
    called = {"value": False}

    def fake_handle_close(message: LandmarkExtractorTerminalInput) -> None:
        called["value"] = True

    monkeypatch.setattr(service, "_handle_close", fake_handle_close)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=uuid4(),
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    asyncio.run(service.handle_message(message))

    assert called["value"] is True


def test_handle_message_routes_capture_abort_to_handle_abort(monkeypatch):
    called = {"value": False}

    def fake_handle_abort(message: LandmarkExtractorTerminalInput) -> None:
        called["value"] = True

    monkeypatch.setattr(service, "_handle_abort", fake_handle_abort)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=uuid4(),
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    asyncio.run(service.handle_message(message))

    assert called["value"] is True


def test_handle_message_raises_for_unsupported_event():
    class DummyMessage:
        event = "unsupported.event"

    message = DummyMessage()  # intentionally not a schema instance

    with pytest.raises(service.LandmarkExtractorServiceError):
        asyncio.run(service.handle_message(message))  # type: ignore[arg-type]
