# apps/landmark_extractor/tests/test_service_close_failure.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from apps.landmark_extractor.config import FEATURE_DIM
from apps.landmark_extractor.domain import CaptureState
from schemas import LandmarkExtractorTerminalInput


def test_handle_close_raises_finalize_error_when_feature_matrix_empty():
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


def test_handle_close_raises_finalize_error_when_feature_row_dim_mismatch():
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    # Create a row with incorrect dimension
    bad_row = [0.1] * (FEATURE_DIM - 1)

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[bad_row],
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


def test_handle_close_raises_finalize_error_when_artifact_write_fails(monkeypatch):
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
        raise RuntimeError("artifact write failure")

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)

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

    # state should still exist because finalize failed
    assert capture_id in service._ACTIVE_CAPTURES
    assert capture_id not in service._TERMINAL_CAPTURE_IDS


def test_handle_close_rolls_back_artifact_when_append_event_fails(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()
    deleted = {"called": False, "artifact_path": None}

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
        raise RuntimeError("append failure")

    def fake_delete_feature_artifact(*, artifact_path: str):
        deleted["called"] = True
        deleted["artifact_path"] = artifact_path

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)
    monkeypatch.setattr(
        service, "delete_feature_artifact", fake_delete_feature_artifact
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

    assert deleted["called"] is True
    assert deleted["artifact_path"] == "artifact.npz"


def test_handle_close_preserves_active_state_when_append_event_fails(monkeypatch):
    service._ACTIVE_CAPTURES.clear()
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )
    service._ACTIVE_CAPTURES[capture_id] = existing_state

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
        raise RuntimeError("append failure")

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)
    monkeypatch.setattr(service, "delete_feature_artifact", lambda **kwargs: None)

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

    assert capture_id in service._ACTIVE_CAPTURES
    assert service._ACTIVE_CAPTURES[capture_id] is existing_state


def test_handle_close_does_not_mark_terminal_when_append_event_fails(monkeypatch):
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
        raise RuntimeError("append failure")

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)
    monkeypatch.setattr(service, "delete_feature_artifact", lambda **kwargs: None)

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

    assert capture_id not in service._TERMINAL_CAPTURE_IDS


def test_handle_close_swallows_rollback_delete_failure_and_still_raises_finalize_error(
    monkeypatch,
):
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
        raise RuntimeError("append failure")

    def fake_delete_feature_artifact(**kwargs):
        raise RuntimeError("delete failure")

    monkeypatch.setattr(service, "write_feature_artifact", fake_write_feature_artifact)
    monkeypatch.setattr(service, "append_event", fake_append_event)
    monkeypatch.setattr(
        service, "delete_feature_artifact", fake_delete_feature_artifact
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

    assert capture_id in service._ACTIVE_CAPTURES
    assert capture_id not in service._TERMINAL_CAPTURE_IDS
