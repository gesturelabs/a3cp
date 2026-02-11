# Location: apps/schema_recorder/tests/test_payload_rejection_routes.py

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.schema_recorder.routes.router import router


@pytest.mark.parametrize(
    "extra_fields, expected_substring",
    [
        ({"frame_data": "data:image/jpeg;base64,AAAA"}, "frame_data"),
        ({"audio_format": "base64", "audio_payload": "AAAA"}, "audio_payload"),
        ({"audio_format": "bytes", "audio_payload": "AAAA"}, "audio_payload"),
    ],
)
def test_append_route_rejects_payload_fields_422(
    extra_fields, expected_substring, monkeypatch, tmp_path
) -> None:
    """
    Route must return a deterministic 422 when schema_recorder enforces payload rejection.
    Also ensures no filesystem IO occurs on payload rejection.
    """
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # If repository IO is attempted, fail deterministically.
    def _fail_append_bytes(*args, **kwargs):
        raise AssertionError(
            "repository.append_bytes() must not be called for payload rejection"
        )

    monkeypatch.setattr(
        "apps.schema_recorder.repository.append_bytes", _fail_append_bytes
    )

    # Deterministic path; should not be used on rejection.
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
        **extra_fields,
    }

    resp = client.post("/schema-recorder/append", json=payload)
    assert resp.status_code == 422, resp.text
    assert expected_substring in resp.text
