from datetime import datetime, timezone
from uuid import uuid4

import pytest

from schemas.a3cp_message import A3CPMessage


def valid_payload():
    return {
        "schema_version": "1.0.0",
        "record_id": uuid4(),  # already UUID object
        "user_id": "user_xyz",
        "session_id": "sess_001",
        "timestamp": datetime.now(timezone.utc),  # fixed: pass datetime object
        "modality": "gesture",
        "source": "communicator",
    }


def test_valid_message_parses():
    msg = A3CPMessage(**valid_payload())
    assert msg.user_id == "user_xyz"
    assert msg.schema_version == "1.0.0"


def test_missing_required_field_fails():
    payload = valid_payload()
    del payload["user_id"]
    with pytest.raises(Exception) as exc_info:
        A3CPMessage(**payload)
    assert "user_id" in str(exc_info.value)


def test_extra_field_rejected():
    payload = valid_payload()
    payload["unexpected_field"] = "this should fail"
    with pytest.raises(Exception) as exc_info:
        A3CPMessage(**payload)
    assert "unexpected_field" in str(exc_info.value)
