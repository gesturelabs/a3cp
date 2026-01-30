# apps/session_manager/tests/test_recorded_timestamp_format.py

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import apps.schema_recorder.config as recorder_config
import apps.session_manager.service as sm_service
from schemas import SessionManagerEndInput, SessionManagerStartInput

_TS_MS_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,6}Z$")


def test_recorded_jsonl_timestamp_is_iso_ms_z(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    start_payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
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
        record_id=uuid.uuid4(),
        user_id="test_user",
        session_id=str(start_out.session_id),
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
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

    for line in lines:
        env = json.loads(line)
        ts = env["event"]["timestamp"]
        assert _TS_MS_Z.match(ts), f"timestamp not ISO ms Z: {ts}"
