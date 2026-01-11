# tests/api/test_session_manager_routes.py
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import apps.session_manager.service as sm  # to reset in-memory state
from api.main import app


@pytest.fixture(scope="function", autouse=True)
def reset_sessions():
    sm._sessions.clear()
    yield
    sm._sessions.clear()


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


def _iso_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _start_payload(
    *,
    user_id: str | None = None,
    is_training_data: bool = True,
    performer_id: str | None = None,
    session_notes: str | None = "pytest start",
    training_intent_label: str | None = "hello",
):
    if user_id is None:
        user_id = str(uuid.uuid4())
    if performer_id is None:
        performer_id = str(uuid.uuid4())
    return {
        "schema_version": "1.0.1",  # strict semver
        "record_id": str(uuid.uuid4()),  # UUIDv4
        "user_id": user_id,
        "timestamp": _iso_now_z(),  # input accepts Z or +00:00
        "performer_id": performer_id,
        # 'source' is optional on input; server sets output to 'session_manager'
        "is_training_data": is_training_data,
        "session_notes": session_notes,
        "training_intent_label": training_intent_label,
    }


def _end_payload(*, user_id: str, session_id: str, end_time: datetime | None = None):
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": _iso_now_z(),
        "end_time": end_time.isoformat().replace("+00:00", "Z"),
    }


def test_sessions_start_happy_path(client: TestClient):
    payload = _start_payload()
    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    # invariants
    assert data["user_id"] == payload["user_id"]
    assert data["performer_id"] == payload["performer_id"]
    assert data["is_training_data"] is True
    assert data["source"] == "session_manager"

    # server-minted fields
    assert isinstance(data["session_id"], str) and data["session_id"].startswith(
        "sess_"
    )
    # start_time + timestamp are ISO8601 Z
    assert data["start_time"].endswith("Z")
    assert data["timestamp"].endswith("Z")


def test_sessions_end_happy_path(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    sess = start.json()
    session_id, user_id = sess["session_id"], sess["user_id"]

    end = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=user_id, session_id=session_id),
    )
    assert end.status_code == 200, end.text
    data = end.json()
    assert data["session_id"] == session_id
    assert data["user_id"] == user_id
    assert data["source"] == "session_manager"
    assert data["end_time"].endswith("Z")
    assert data["timestamp"].endswith("Z")


def test_end_requires_session_id_422(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    user_id = start.json()["user_id"]

    bad = _end_payload(user_id=user_id, session_id="")
    bad.pop("session_id")  # omit required field

    r = client.post("/session_manager/sessions.end", json=bad)
    assert r.status_code == 422, r.text  # schema validation error

    detail = r.json()["detail"]
    assert isinstance(detail, list)
    assert any(
        d.get("loc") == ["body", "session_id"] and d.get("type") == "missing"
        for d in detail
    ), detail


def test_end_user_mismatch_404(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    session_id = start.json()["session_id"]

    r = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=str(uuid.uuid4()), session_id=session_id),
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Session not found or user mismatch"


def test_end_session_double_close_400(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    session_id = start.json()["session_id"]
    user_id = start.json()["user_id"]

    r1 = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=user_id, session_id=session_id),
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=user_id, session_id=session_id),
    )
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Session already closed"
