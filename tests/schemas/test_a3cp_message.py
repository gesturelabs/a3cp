# tests/schemas/test_a3cp_message.py
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from schemas.utils.validate import validate_a3cp_message


def test_valid_a3cp_message_passes():
    data = {
        "schema_version": "1.1.0",
        "record_id": str(uuid4()),
        "user_id": "user_xyz",
        "session_id": "sess_2025-07-31_xyz",
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        "modality": "gesture",
        "source": "communicator",
        # Optional fields
        "classifier_output": {"intent": "greet", "confidence": 0.9},
        "context": {"location": "kitchen"},
    }

    msg = validate_a3cp_message(data)
    assert msg.session_id == "sess_2025-07-31_xyz"
    assert msg.schema_version == "1.1.0"
    assert msg.modality == "gesture"
    assert msg.source == "communicator"


def test_missing_required_field_fails():
    data = {
        "schema_version": "1.1.0",
        "record_id": str(uuid4()),
        "user_id": "user_xyz",
        # session_id is missing
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        "modality": "gesture",
        "source": "communicator",
    }

    with pytest.raises(Exception) as exc:
        validate_a3cp_message(data)

    assert "session_id" in str(exc.value)


def test_rejects_invalid_modality():
    data = {
        "schema_version": "1.1.0",
        "record_id": str(uuid4()),
        "user_id": "user_xyz",
        "session_id": "sess_x",
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        "modality": "telepathy",  # Invalid
        "source": "system",
    }

    with pytest.raises(Exception) as exc:
        validate_a3cp_message(data)

    assert "telepathy" in str(exc.value)
