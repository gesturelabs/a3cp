# apps/session_manager/tests/test_system_performer_id.py

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import apps.schema_recorder.config as recorder_config
import apps.session_manager.service as sm_service
from schemas import SessionManagerEndInput, SessionManagerStartInput


def test_system_performer_id_allowed_and_recorded(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    start_payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="system",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )
    start_out = sm_service.start_session(start_payload)

    end_payload = SessionManagerEndInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        session_id=str(start_out.session_id),
        timestamp=datetime.now(timezone.utc),
        performer_id="system",
        end_time=datetime.now(timezone.utc),
    )
    sm_service.end_session(end_payload)

    log_path = (
        recorder_config.LOG_ROOT
        / "users"
        / "test_user"
        / "sessions"
        / f"{start_out.session_id}.jsonl"
    )

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    e1 = json.loads(lines[0])["event"]
    e2 = json.loads(lines[1])["event"]

    assert e1["performer_id"] == "system"
    assert e2["performer_id"] == "system"
