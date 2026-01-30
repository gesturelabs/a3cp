# apps/session_manager/tests/test_boundary_event_contract.py

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import apps.schema_recorder.config as recorder_config
import apps.session_manager.service as sm_service
from schemas import SessionManagerStartInput

_TS_MS_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


def _assert_uuid4(val: str) -> None:
    u = uuid.UUID(val)
    assert u.version == 4


def test_start_emitted_boundary_event_contract(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid4(),  # input may contain record_id, but output must be server-authoritative
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )

    out = sm_service.start_session(payload)

    assert out.source == "session_manager"
    assert str(out.user_id).strip() != ""
    assert str(out.session_id).strip() != ""
    _assert_uuid4(str(out.record_id))

    # Emitted object is datetime-typed; enforce UTC + ms precision (format enforced at serialization)
    assert out.timestamp.tzinfo is not None
    offset = out.timestamp.utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 0
    assert out.timestamp.microsecond % 1000 == 0
