# apps/session_manager/tests/test_service.py

# tests/test_service.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

import apps.session_manager.service as sm_service
from apps.schema_recorder.service import RecorderIOError
from schemas import SessionManagerStartInput


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
