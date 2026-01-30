# apps/session_manager/tests/test_atomic_recording_semantics.py

import uuid
from datetime import datetime, timezone

import pytest

from apps.session_manager.service import end_session, start_session
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_start_append_failure_creates_no_active_session(tmp_path, monkeypatch):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Force recorder failure at append boundary
    def _append_fail(*args, **kwargs):
        raise RuntimeError("forced append failure")

    monkeypatch.setattr(sm_service, "append_event", _append_fail)

    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        is_training_data=False,
        session_notes=None,
        performer_id="tester",
        training_intent_label=None,
    )

    with pytest.raises(RuntimeError, match="forced append failure"):
        sm_service.start_session(payload)

    # Atomicity: no active session created if append fails
    assert sm_service._sessions == {}

    # (Optional check) no session JSONL file exists (append failed)
    sessions_dir = recorder_config.LOG_ROOT / "users" / "test_user" / "sessions"
    if sessions_dir.exists():
        assert list(sessions_dir.glob("*.jsonl")) == []


def test_end_append_failure_does_not_close_session(tmp_path, monkeypatch):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Start a real session (append START succeeds)
    start_payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        is_training_data=False,
        session_notes=None,
        performer_id="tester",
        training_intent_label=None,
    )
    start_out = start_session(start_payload)
    sid = str(start_out.session_id)

    # Force recorder failure on END append
    def _append_fail(*args, **kwargs):
        raise RuntimeError("forced append failure")

    monkeypatch.setattr(sm_service, "append_event", _append_fail)

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        session_id=sid,
        timestamp=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        performer_id="tester",
    )

    with pytest.raises(RuntimeError, match="forced append failure"):
        end_session(end_payload)

    # Atomicity: session remains active if append fails
    sess = sm_service._sessions[sid]
    assert sess["status"] == "active"
    assert "end_time" not in sess
