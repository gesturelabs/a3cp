# apps/session_manager/tests/test_no_record_on_output_validation_failure.py

import uuid
from datetime import datetime, timezone

import pytest

from apps.session_manager.service import end_session, start_session
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_start_no_side_effects_if_output_construction_fails(tmp_path, monkeypatch):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Force boundary-output construction to fail before any mkdir/append/state mutation.
    def _boom(*args, **kwargs):
        raise ValueError("forced output construction failure")

    monkeypatch.setattr(sm_service, "SessionManagerStartOutput", _boom)

    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),  # client-supplied (must not matter here)
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        is_training_data=False,
        session_notes=None,
        performer_id="tester",
        training_intent_label=None,
    )

    with pytest.raises(ValueError, match="forced output construction failure"):
        sm_service.start_session(payload)

    # No in-memory mutation
    assert sm_service._sessions == {}

    # No JSONL append attempted (file absent)
    sessions_dir = recorder_config.LOG_ROOT / "users" / "test_user" / "sessions"
    assert not sessions_dir.exists()


def test_end_no_side_effects_if_output_construction_fails(tmp_path, monkeypatch):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Create a real session (this will mkdir + append the START event).
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

    log_path = (
        recorder_config.LOG_ROOT
        / "users"
        / "test_user"
        / "sessions"
        / f"{str(start_out.session_id)}.jsonl"
    )
    assert log_path.exists()
    before_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(before_lines) == 1  # only START so far

    # Force END boundary-output construction to fail before append/state mutation.
    def _boom(*args, **kwargs):
        raise ValueError("forced end output construction failure")

    monkeypatch.setattr(sm_service, "SessionManagerEndOutput", _boom)

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        session_id=str(start_out.session_id),
        timestamp=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        performer_id="tester",
    )

    with pytest.raises(ValueError, match="forced end output construction failure"):
        end_session(end_payload)

    # No JSONL append attempted (still exactly one line)
    after_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert after_lines == before_lines

    # No in-memory mutation (session still active, no end_time written)
    sess = sm_service._sessions[str(start_out.session_id)]
    assert sess["status"] == "active"
    assert "end_time" not in sess
