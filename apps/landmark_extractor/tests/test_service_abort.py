# apps/landmark_extractor/tests/test_service_abort.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from apps.landmark_extractor.config import FEATURE_DIM
from apps.landmark_extractor.domain import CaptureState
from schemas import LandmarkExtractorTerminalInput


def test_handle_abort_rejects_terminal_capture():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()
    service._TERMINAL_CAPTURE_IDS.add(capture_id)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._handle_abort(message)


def test_handle_abort_raises_for_unknown_capture():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()
    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._handle_abort(message)


def test_handle_abort_clears_active_state():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    service._handle_abort(message)

    assert capture_id not in service._ACTIVE_CAPTURES


def test_handle_abort_marks_capture_terminal():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    service._handle_abort(message)

    assert capture_id in service._TERMINAL_CAPTURE_IDS


def test_handle_abort_writes_no_artifact(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    def fail_write(**kwargs):
        raise AssertionError("write_feature_artifact should not be called")

    monkeypatch.setattr(service, "write_feature_artifact", fail_write)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    service._handle_abort(message)


def test_handle_abort_emits_no_event(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    def fail_append(**kwargs):
        raise AssertionError("append_event should not be called")

    monkeypatch.setattr(service, "append_event", fail_append)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.abort",
        timestamp_end=now,
        error_code="capture_aborted",
    )

    service._handle_abort(message)
