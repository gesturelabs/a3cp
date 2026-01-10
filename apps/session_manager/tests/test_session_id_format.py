# apps/session_manager/tests/test_session_id_format.py

import re
import uuid
from datetime import datetime, timezone

from apps.session_manager.service import start_session
from schemas import SessionManagerStartInput


def test_session_id_format_and_uniqueness():
    """
    Sprint 1 invariant:
    - session_id format is: 'sess_' + 16 lowercase hex chars
    - generated session_ids are unique within the running process
    """
    pattern = re.compile(r"^sess_[0-9a-f]{16}$")
    seen: set[str] = set()

    for _ in range(200):
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

        out = start_session(payload)

        assert out.session_id, "session_id must be non-empty"
        assert pattern.match(out.session_id), f"unexpected session_id: {out.session_id}"
        assert out.session_id not in seen, "duplicate session_id generated"
        seen.add(out.session_id)
