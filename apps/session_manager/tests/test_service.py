# apps/session_manager/tests/test_service.py


from __future__ import annotations

import builtins
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

import apps.schema_recorder.config as recorder_config
import apps.session_manager.service as sm_service
from apps.schema_recorder.service import MissingSessionPath, RecorderIOError
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_start_session_no_state_change_on_recorder_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Ensure clean in-memory state (demo-only store)
    sm_service._sessions.clear()

    def _fail_append_event(*, user_id: str, session_id: str, message) -> None:
        raise RecorderIOError("forced recorder failure")

    # Patch the symbol used by session_manager (it imports append_event into its module namespace)
    monkeypatch.setattr(sm_service, "append_event", _fail_append_event)

    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        # optional fields (include if your StartInput requires them)
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )

    with pytest.raises(RecorderIOError):
        sm_service.start_session(payload)

    # Assert: no session was committed as active (and ideally no entry created at all)
    assert sm_service._sessions == {}


def test_end_session_no_state_change_on_missing_sessions_dir(tmp_path: Path) -> None:
    import apps.schema_recorder.config as recorder_config

    # Point logs at tmp_path and ensure clean in-memory state
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Start a session normally (this will mkdir users/<user>/sessions and append a start event)
    start_payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )
    start_out = sm_service.start_session(start_payload)
    session_id = str(start_out.session_id)

    # Remove the sessions directory to simulate recorder preflight failure
    sessions_dir = recorder_config.LOG_ROOT / "users" / "test_user" / "sessions"
    assert sessions_dir.exists()
    sessions_dir.rename(sessions_dir.with_name("sessions__missing"))
    assert not sessions_dir.exists()

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="test_user",
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        end_time=datetime.now(timezone.utc),
    )

    with pytest.raises(MissingSessionPath):
        sm_service.end_session(end_payload)

    # Assert: session remains active and not closed
    assert sm_service._sessions[session_id]["status"] == "active"
    assert "end_time" not in sm_service._sessions[session_id]


def test_session_manager_never_opens_jsonl_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    real_open = builtins.open

    def _guarded_open(file, *args, **kwargs):
        p = str(file)
        if p.endswith(".jsonl"):
            raise AssertionError(f"session_manager attempted to open a JSONL file: {p}")
        return real_open(file, *args, **kwargs)

    # Patch open in the session_manager module namespace only
    monkeypatch.setattr(sm_service, "open", _guarded_open, raising=False)

    start_payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )
    start_out = sm_service.start_session(start_payload)

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="test_user",
        session_id=str(start_out.session_id),
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        end_time=datetime.now(timezone.utc),
    )
    sm_service.end_session(end_payload)
