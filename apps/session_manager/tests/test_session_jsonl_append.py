# apps/session_manager/tests/test_session_jsonl_append.py

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from apps.session_manager.service import end_session, start_session
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_start_end_appends_two_ordered_events(tmp_path):
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
