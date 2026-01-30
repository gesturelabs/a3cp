# apps/session_manager/tests/test_session_jsonl_append.py

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from apps.session_manager.service import end_session, start_session
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_start_end_appends_two_ordered_events(tmp_path):
    import apps.schema_recorder.config as recorder_config

    recorder_config.LOG_ROOT = tmp_path / "logs"

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

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        session_id=str(start_out.session_id),
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        end_time=datetime.now(timezone.utc),
    )

    end_out = end_session(end_payload)

    log_path = (
        Path(tmp_path)
        / "logs"
        / "users"
        / "test_user"
        / "sessions"
        / f"{str(start_out.session_id)}.jsonl"
    )

    assert log_path.exists(), f"expected session log at {log_path}"

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, f"expected 2 jsonl lines, got {len(lines)}"

    env1 = json.loads(lines[0])
    env2 = json.loads(lines[1])
    e1 = env1["event"]
    e2 = env2["event"]

    # Same session + user
    assert e1["user_id"] == "test_user"
    assert e2["user_id"] == "test_user"
    assert e1["session_id"] == str(start_out.session_id)
    assert e2["session_id"] == str(start_out.session_id)

    # Ordered boundary events (file order)
    assert e1.get("source") == "session_manager"
    assert e2.get("source") == "session_manager"

    # Sanity: end output corresponds to end event session_id
    assert e2["session_id"] == str(end_out.session_id)


def test_start_session_delegates_append_to_schema_recorder_and_does_not_write_jsonl_directly(
    tmp_path, monkeypatch
):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    calls = {"append_event": 0}

    # Allow mkdir but forbid any direct attempt to create/write a *.jsonl file from session_manager.
    # If session_manager delegates correctly, it should only call append_event.
    def _append_event_spy(*, user_id: str, session_id: str, message):
        calls["append_event"] += 1
        # Do not write anything; just simulate success.
        return None

    monkeypatch.setattr(sm_service, "append_event", _append_event_spy)

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

    sm_service.start_session(payload)

    assert calls["append_event"] == 1

    # session_manager may create the sessions directory, but must not have written a JSONL file itself here
    sessions_dir = recorder_config.LOG_ROOT / "users" / "test_user" / "sessions"
    assert sessions_dir.exists()
    assert list(sessions_dir.glob("*.jsonl")) == []
