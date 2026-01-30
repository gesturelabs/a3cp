# apps/session_manager/tests/test_authority_hardening.py

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import apps.schema_recorder.config as recorder_config
import apps.session_manager.service as sm_service
from schemas import SessionManagerStartInput


def _is_uuid4(val: str) -> bool:
    u = uuid.UUID(val)
    return u.version == 4


def test_input_cannot_override_server_record_id(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    input_record_id = uuid.uuid4()
    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=input_record_id,
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )

    out = sm_service.start_session(payload)

    assert str(out.record_id) != str(input_record_id)
    assert _is_uuid4(str(out.record_id))


def test_input_cannot_override_server_timestamp(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    fake_past = datetime.now(timezone.utc) - timedelta(days=365)
    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        timestamp=fake_past,
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
    )

    out = sm_service.start_session(payload)

    # Must not echo input timestamp
    assert out.timestamp != fake_past

    # Must be near "now" (loose bound to avoid flakiness)
    now = datetime.now(timezone.utc)
    assert abs((now - out.timestamp).total_seconds()) < 5


def test_input_cannot_override_source(tmp_path: Path) -> None:
    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    payload = SessionManagerStartInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="test_user",
        timestamp=datetime.now(timezone.utc),
        performer_id="tester",
        is_training_data=False,
        session_notes=None,
        training_intent_label=None,
        # If StartInput allows source, attempt to override; if it forbids extra fields,
        # this test will fail and should be removed or adapted to your input model policy.
        source="evil_client",
    )

    out = sm_service.start_session(payload)

    assert out.source == "session_manager"
