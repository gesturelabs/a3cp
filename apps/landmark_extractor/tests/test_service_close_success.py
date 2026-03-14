# apps/landmark_extractor/tests/test_service_close_success.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from apps.landmark_extractor.config import FEATURE_DIM
from apps.landmark_extractor.domain import CaptureState
from schemas import LandmarkExtractorTerminalInput


def test_handle_close_rejects_terminal_capture():
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
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._handle_close(message)


def test_handle_close_raises_for_unknown_capture():
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
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._handle_close(message)


def test_handle_close_raises_when_feature_rows_empty():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[],
    )

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    with pytest.raises(service.LandmarkExtractorFinalizeError):
        service._handle_close(message)


def test_handle_close_writes_artifact_before_append_event(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    call_order = []

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    def fake_write_feature_artifact(**kwargs):
        call_order.append("artifact")
        return service.ArtifactWriteResult(
            capture_id=capture_id,
            artifact_path="test.npz",
            artifact_hash="sha256:abc",
            shape=(1, FEATURE_DIM),
            dtype="float32",
            format="npz",
        )

    def fake_append_event(**kwargs):
        call_order.append("event")

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    service._handle_close(message)

    assert call_order == ["artifact", "event"]


def test_handle_close_builds_and_appends_raw_features_ready_message(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    captured = {"message": None, "user_id": None, "session_id": None}

    def fake_write_feature_artifact(**kwargs):
        return service.ArtifactWriteResult(
            capture_id=capture_id,
            artifact_path="artifact.npz",
            artifact_hash="sha256:abc",
            shape=(1, FEATURE_DIM),
            dtype="float32",
            format="npz",
        )

    def fake_append_event(**kwargs):
        captured["message"] = kwargs["message"]
        captured["user_id"] = kwargs["user_id"]
        captured["session_id"] = kwargs["session_id"]

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    service._handle_close(message)

    appended = captured["message"]
    assert appended is not None
    assert appended.event == "raw_features.ready"
    assert appended.user_id == "user-1"
    assert str(appended.session_id) == "session-1"
    assert appended.capture_id == capture_id
    assert appended.modality == "gesture"
    assert appended.source == "landmark_extractor"
    assert appended.performer_id == "system"
    assert appended.timestamp == now

    assert captured["user_id"] == "user-1"
    assert captured["session_id"] == "session-1"

    assert appended.raw_features_ref.uri == "artifact.npz"
    assert appended.raw_features_ref.hash == "sha256:abc"
    assert appended.raw_features_ref.encoding == service.FEATURE_ENCODING_ID
    assert appended.raw_features_ref.shape == [1, FEATURE_DIM]
    assert appended.raw_features_ref.dtype == "float32"
    assert appended.raw_features_ref.format == "npz"


def test_handle_close_clears_active_state_after_success(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    def fake_write_feature_artifact(**kwargs):
        return service.ArtifactWriteResult(
            capture_id=capture_id,
            artifact_path="artifact.npz",
            artifact_hash="sha256:abc",
            shape=(1, FEATURE_DIM),
            dtype="float32",
            format="npz",
        )

    def fake_append_event(**kwargs):
        return None

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    service._handle_close(message)

    assert capture_id not in service._ACTIVE_CAPTURES


def test_handle_close_marks_capture_terminal_after_success(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    def fake_write_feature_artifact(**kwargs):
        return service.ArtifactWriteResult(
            capture_id=capture_id,
            artifact_path="artifact.npz",
            artifact_hash="sha256:abc",
            shape=(1, FEATURE_DIM),
            dtype="float32",
            format="npz",
        )

    def fake_append_event(**kwargs):
        return None

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorTerminalInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        event="capture.close",
        timestamp_end=now,
        error_code=None,
    )

    service._handle_close(message)

    assert capture_id in service._TERMINAL_CAPTURE_IDS
