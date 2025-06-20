# tests/schemas/test_raw_action_record.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from schemas.raw_action_record import RawActionRecord


def test_valid_record() -> None:
    now = datetime.now(tz=timezone.utc)
    record = RawActionRecord(
        # Optional fields omitted intentionally
        schema_version="1.0",
        record_id=uuid4(),
        user_id="user01",
        session_id="sess_2025_01",
        timestamp=now,
        modality="gesture",
        source="communicator",
    )

    assert isinstance(record, RawActionRecord)
    assert record.schema_version == "1.0"
    assert record.user_id == "user01"
    assert record.timestamp == now


def test_missing_required_field() -> None:
    with pytest.raises(ValidationError, match="record_id"):
        RawActionRecord(
            # Optional fields omitted intentionally
            schema_version="1.0",
            # record_id is missing
            user_id="elias01",
            session_id="sess_abc123",
            timestamp=datetime.now(tz=timezone.utc),
            modality="gesture",
            source="communicator",
        )


def test_extra_field_rejected() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        RawActionRecord(
            # Optional fields omitted intentionally
            schema_version="1.0",
            record_id=uuid4(),
            user_id="elias01",
            session_id="sess_abc123",
            timestamp=datetime.now(tz=timezone.utc),
            modality="gesture",
            source="communicator",
            unexpected_field="nope",  # should trigger extra field rejection
        )
