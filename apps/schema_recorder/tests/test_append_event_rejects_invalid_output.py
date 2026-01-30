# apps/schema_recorder/tests/test_append_event_rejects_invalid_output.py

import uuid
from datetime import datetime, timezone

import pytest

from apps.schema_recorder.service import append_event
from schemas import BaseSchema


class BadEvent(BaseSchema):
    # minimal subclass but we will break serialization deterministically
    pass


def test_append_event_fails_fast_and_writes_nothing_on_serialization_error(
    tmp_path, monkeypatch
):
    import apps.schema_recorder.config as recorder_config

    recorder_config.LOG_ROOT = tmp_path / "logs"

    # Pre-create parent session directory (recorder requires it)
    log_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    log_dir.mkdir(parents=True)

    log_path = log_dir / "s1.jsonl"

    msg = BadEvent(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="u1",
        timestamp=datetime.now(timezone.utc),
    )

    # Force model_dump to fail → deterministic invalid output payload
    monkeypatch.setattr(
        BadEvent,
        "model_dump",
        lambda self, *a, **k: (_ for _ in ()).throw(ValueError("boom")),
    )

    with pytest.raises(ValueError, match="boom"):
        append_event(user_id="u1", session_id="s1", message=msg)

    # JSONL must not exist or must be empty
    assert not log_path.exists() or log_path.read_text(encoding="utf-8") == ""
