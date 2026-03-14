# apps/landmark_extractor/tests/test_service_frame.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from apps.landmark_extractor.domain import CaptureState, NormalizedLandmarks
from schemas import LandmarkExtractorFrameInput


def test_handle_frame_creates_new_capture_state_on_first_frame(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    monkeypatch.setattr(service, "_decode_frame_data", lambda frame_data: object())
    monkeypatch.setattr(
        service._BACKEND,
        "extract_landmarks",
        lambda frame, timestamp_frame: NormalizedLandmarks(),
    )
    monkeypatch.setattr(service, "build_feature_row", lambda landmarks: [0.1] * 176)

    capture_id = uuid4()
    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    service._handle_frame(message)

    assert capture_id in service._ACTIVE_CAPTURES

    state = service._ACTIVE_CAPTURES[capture_id]
    assert state.capture_id == capture_id
    assert state.user_id == "user-1"
    assert state.session_id == "session-1"
    assert state.feature_rows == [[0.1] * 176]


def test_handle_frame_appends_feature_row_to_existing_capture(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    monkeypatch.setattr(service, "_decode_frame_data", lambda frame_data: object())
    monkeypatch.setattr(
        service._BACKEND,
        "extract_landmarks",
        lambda frame, timestamp_frame: NormalizedLandmarks(),
    )
    monkeypatch.setattr(service, "build_feature_row", lambda landmarks: [0.2] * 176)

    capture_id = uuid4()
    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * 176],
    )
    service._ACTIVE_CAPTURES[capture_id] = existing_state

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=2,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    service._handle_frame(message)

    state = service._ACTIVE_CAPTURES[capture_id]
    assert state is existing_state
    assert state.feature_rows == [[0.1] * 176, [0.2] * 176]


def test_handle_frame_rejects_frame_for_terminal_capture():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()
    service._TERMINAL_CAPTURE_IDS.add(capture_id)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._handle_frame(message)


def test_handle_frame_preserves_state_when_decode_fails(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * 176],
    )
    service._ACTIVE_CAPTURES[capture_id] = existing_state

    def fake_decode(_):
        raise service.LandmarkExtractorFrameError("decode failure")

    monkeypatch.setattr(service, "_decode_frame_data", fake_decode)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=2,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._handle_frame(message)

    state = service._ACTIVE_CAPTURES[capture_id]

    assert state is existing_state
    assert state.feature_rows == [[0.1] * 176]


def test_handle_frame_raises_frame_error_when_backend_extraction_fails(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    monkeypatch.setattr(service, "_decode_frame_data", lambda _: object())

    def fake_extract_landmarks(frame, timestamp_frame):
        raise service.MediaPipeExtractionError("backend failure")

    monkeypatch.setattr(service._BACKEND, "extract_landmarks", fake_extract_landmarks)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._handle_frame(message)

    assert capture_id in service._ACTIVE_CAPTURES
    state = service._ACTIVE_CAPTURES[capture_id]
    assert state.feature_rows == []


def test_handle_frame_raises_frame_error_when_feature_row_build_fails(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    monkeypatch.setattr(service, "_decode_frame_data", lambda _: object())
    monkeypatch.setattr(
        service._BACKEND,
        "extract_landmarks",
        lambda frame, ts: NormalizedLandmarks(),
    )

    def fake_build_feature_row(_):
        raise ValueError("feature build failure")

    monkeypatch.setattr(service, "build_feature_row", fake_build_feature_row)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._handle_frame(message)

    assert capture_id in service._ACTIVE_CAPTURES
    state = service._ACTIVE_CAPTURES[capture_id]
    assert state.feature_rows == []


def test_handle_frame_does_not_append_row_on_processing_failure(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * 176],
    )
    service._ACTIVE_CAPTURES[capture_id] = existing_state

    monkeypatch.setattr(service, "_decode_frame_data", lambda _: object())

    def fake_extract_landmarks(frame, ts):
        raise service.MediaPipeExtractionError("backend failure")

    monkeypatch.setattr(service._BACKEND, "extract_landmarks", fake_extract_landmarks)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=2,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._handle_frame(message)

    state = service._ACTIVE_CAPTURES[capture_id]

    assert state.feature_rows == [[0.1] * 176]
