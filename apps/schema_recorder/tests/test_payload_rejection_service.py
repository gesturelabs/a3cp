# Location: apps/schema_recorder/tests/test_payload_rejection_service.py

import uuid

import pytest

from apps.schema_recorder import service
from schemas import A3CPMessage


@pytest.mark.parametrize(
    "extra_fields",
    [
        {"frame_data": "data:image/jpeg;base64,AAAA"},  # transport-only image payload
        {
            "audio_format": "base64",
            "audio_payload": "AAAA",
        },  # transport-only audio payload
        {
            "audio_format": "bytes",
            "audio_payload": "AAAA",
        },  # transport-only audio payload
    ],
)
def test_append_event_rejects_payload_fields_before_io(
    monkeypatch, tmp_path, extra_fields
) -> None:
    """
    Safety invariant: payload-bearing events must be rejected at the single-writer boundary
    before any repository IO is attempted.
    """

    # If IO is attempted, fail the test deterministically.
    def _fail_append_bytes(*args, **kwargs):
        raise AssertionError(
            "repository.append_bytes() must not be called for payload rejection"
        )

    monkeypatch.setattr(
        "apps.schema_recorder.repository.append_bytes", _fail_append_bytes
    )

    # Path resolution should not matter because we must reject before IO; keep deterministic anyway.
    monkeypatch.setattr(
        "utils.paths.session_log_path",
        lambda *, log_root, user_id, session_id: tmp_path / "should_not_write.jsonl",
    )

    payload = {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": "u1",
        "session_id": "s1",
        "timestamp": "2025-06-15T12:34:56.789Z",
        "source": "schema_recorder_test",
        "modality": "audio",
        **extra_fields,  # allowed by A3CPMessage extra="allow"
    }

    msg = A3CPMessage(**payload)

    assert msg.session_id is not None

    with pytest.raises(service.PayloadNotAllowed):
        service.append_event(
            user_id=msg.user_id, session_id=msg.session_id, message=msg
        )
