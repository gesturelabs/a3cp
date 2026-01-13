# apps/session_manager/tests/test_event_invariants.py

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from apps.session_manager.service import end_session, start_session
from schemas import SessionManagerEndInput, SessionManagerStartInput


def _assert_common_invariants(event: dict) -> None:
    # Required keys exist
    for key in [
        "source",
        "user_id",
        "session_id",
        "timestamp",
        "record_id",
        "performer_id",
    ]:
        assert key in event, f"missing key: {key}"

    # Required values are non-empty (and not null)
    assert event["source"] == "session_manager"
    assert isinstance(event["user_id"], str) and event["user_id"].strip()
    assert isinstance(event["session_id"], str) and event["session_id"].strip()

    # These will likely be strings in JSONL; validate they are present and non-empty.
    assert event["timestamp"], "timestamp must be present"
    assert event["record_id"], "record_id must be present"

    # performer_id invariant (this is the one most likely to fail right now)
    assert isinstance(event["performer_id"], str) and event["performer_id"].strip()


def test_session_manager_events_enforce_common_invariants(tmp_path, monkeypatch):
    import apps.session_manager.repository as session_repo

    session_repo.LOG_ROOT = tmp_path / "logs"

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
        end_time=datetime.now(timezone.utc),
        performer_id="tester",
    )
    end_session(end_payload)

    log_path = (
        Path(tmp_path)
        / "logs"
        / "users"
        / "test_user"
        / "sessions"
        / f"{str(start_out.session_id)}.jsonl"
    )
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    env1 = json.loads(lines[0])
    env2 = json.loads(lines[1])

    _assert_common_invariants(env1["event"])
    _assert_common_invariants(env2["event"])
