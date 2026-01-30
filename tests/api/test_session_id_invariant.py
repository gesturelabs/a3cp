# tests/api/test_session_id_invariant.py

import uuid
from datetime import datetime, timezone

import pytest


def _iso_z_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _start_payload(*, user_id: str) -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": user_id,
        "timestamp": _iso_z_now(),
        "performer_id": "tester",
        "is_training_data": False,
        "session_notes": None,
        "training_intent_label": None,
    }


def _end_payload(*, user_id: str, session_id: str) -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": _iso_z_now(),
        "performer_id": "tester",
        "end_time": _iso_z_now(),
    }


@pytest.mark.anyio
async def test_end_returns_same_session_id(async_client) -> None:
    user_id = f"u_{uuid.uuid4()}"
    start = await async_client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )

    assert start.status_code == 200, start.text
    sess = start.json()
    session_id, user_id = sess["session_id"], sess["user_id"]

    end = await async_client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=user_id, session_id=session_id),
    )
    assert end.status_code == 200, end.text
    assert end.json()["session_id"] == session_id


@pytest.mark.anyio
async def test_end_rejects_unknown_session_id(async_client) -> None:

    user_id = f"u_{uuid.uuid4()}"
    start = await async_client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )

    assert start.status_code == 200, start.text
    user_id = start.json()["user_id"]

    bad_session_id = "sess_deadbeefdeadbeef"

    end = await async_client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=user_id, session_id=bad_session_id),
    )

    # Your current semantics likely return 404 here; change to 400 only if you add an explicit API rule.
    assert end.status_code in (400, 404), end.text
