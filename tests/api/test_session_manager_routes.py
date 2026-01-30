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


def _end_payload(*, user_id: str, session_id: str) -> dict:
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "performer_id": "tester",
        "end_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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


def test_sessions_start_record_id_is_server_generated_not_client(client: TestClient):
    payload = _start_payload()
    client_record_id = str(uuid.uuid4())
    payload["record_id"] = client_record_id

    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["record_id"] != client_record_id

    # sanity: response record_id is a UUID string
    uuid.UUID(data["record_id"])


def test_sessions_start_source_and_timestamp_are_server_authoritative(
    client: TestClient,
):
    payload = _start_payload()

    # adversarial client-supplied fields
    payload["source"] = "evil_client"
    payload["timestamp"] = "1999-01-01T00:00:00.000Z"

    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    # source is server-authoritative
    assert data["source"] == "session_manager"

    # timestamp is server-authoritative (must not echo input)
    assert data["timestamp"] != payload["timestamp"]
    assert data["timestamp"].endswith("Z")


def test_sessions_end_record_id_is_server_generated_not_client(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    sess = start.json()
    session_id, user_id = sess["session_id"], sess["user_id"]

    payload = _end_payload(user_id=user_id, session_id=session_id)
    client_record_id = str(uuid.uuid4())
    payload["record_id"] = client_record_id

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["record_id"] != client_record_id

    # sanity: response record_id is a UUID string
    uuid.UUID(data["record_id"])


def test_sessions_start_and_end_record_ids_are_unique(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    start_data = start.json()

    end = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(
            user_id=start_data["user_id"],
            session_id=start_data["session_id"],
        ),
    )
    assert end.status_code == 200, end.text
    end_data = end.json()

    assert start_data["record_id"] != end_data["record_id"]


def test_sessions_start_rejects_second_active_session_for_same_user_409(
    client: TestClient,
):
    user_id = str(uuid.uuid4())

    r1 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["detail"] == "User already has an active session"


def test_sessions_end_source_and_timestamp_are_server_authoritative(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    sess = start.json()
    session_id, user_id = sess["session_id"], sess["user_id"]

    payload = _end_payload(user_id=user_id, session_id=session_id)

    # adversarial client-supplied fields
    payload["source"] = "evil_client"
    payload["timestamp"] = "1999-01-01T00:00:00.000Z"

    end = client.post("/session_manager/sessions.end", json=payload)
    assert end.status_code == 200, end.text
    data = end.json()

    # source is server-authoritative
    assert data["source"] == "session_manager"

    # timestamp is server-authoritative (must not echo input)
    assert data["timestamp"] != payload["timestamp"]
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


def test_end_user_mismatch_403(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    session_id = start.json()["session_id"]

    r = client.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id=str(uuid.uuid4()), session_id=session_id),
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Session user mismatch"


def test_end_session_double_close_409(client: TestClient):
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
    assert r2.status_code == 409
    assert r2.json()["detail"] == "Session already closed"


def test_sessions_start_allows_different_user_while_first_active_200(
    client: TestClient,
):
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())

    r1 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_a)
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_b)
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["user_id"] == user_b


def test_sessions_start_output_validation_failure_causes_500_and_no_side_effects(
    client: TestClient, tmp_path, monkeypatch
):
    # Point logs to tmp and clear in-memory state
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    # Deterministic forcing strategy:
    # return an invalid session_id (None) so SessionManagerStartOutput validation fails.
    monkeypatch.setattr(sm_service, "generate_session_id", lambda: None)

    payload = _start_payload(user_id="test_user")

    c = TestClient(app, raise_server_exceptions=False)
    r = c.post("/session_manager/sessions.start", json=payload)

    # Unhandled validation error -> 500
    assert r.status_code == 500, r.text

    # No in-memory mutation
    assert sm_service._sessions == {}

    # No JSONL append attempted (file absent)
    sessions_dir = recorder_config.LOG_ROOT / "users" / "test_user" / "sessions"
    assert not sessions_dir.exists()


def test_sessions_end_output_validation_failure_causes_500_and_no_side_effects(
    tmp_path, monkeypatch
):
    from fastapi.testclient import TestClient

    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service
    from api.main import app

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    c = TestClient(app, raise_server_exceptions=False)

    # First create a valid session (writes 1 START event)
    start = c.post(
        "/session_manager/sessions.start", json=_start_payload(user_id="test_user")
    )
    assert start.status_code == 200, start.text
    start_data = start.json()

    log_path = (
        recorder_config.LOG_ROOT
        / "users"
        / "test_user"
        / "sessions"
        / f'{start_data["session_id"]}.jsonl'
    )
    before = log_path.read_text(encoding="utf-8")

    # Deterministic forcing seam: break END output construction
    monkeypatch.setattr(
        sm_service,
        "SessionManagerEndOutput",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")),
    )

    payload = _end_payload(
        user_id="test_user",
        session_id=start_data["session_id"],
    )

    r = c.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 500, r.text

    # JSONL unchanged (no END append)
    after = log_path.read_text(encoding="utf-8")
    assert after == before

    # In-memory unchanged (still active)
    sess = sm_service._sessions[start_data["session_id"]]
    assert sess["status"] == "active"
    assert "end_time" not in sess


def test_sessions_end_allows_system_initiated_closure_with_authoritative_fields(
    client: TestClient,
):
    # start normal session
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    s = start.json()
    session_id, user_id = s["session_id"], s["user_id"]
    start_record_id = s["record_id"]

    # system-initiated end: adversarial client-supplied fields included
    payload = _end_payload(user_id=user_id, session_id=session_id)
    payload["performer_id"] = "system"
    payload["record_id"] = str(uuid.uuid4())  # must be ignored
    payload["timestamp"] = "1999-01-01T00:00:00.000Z"  # must be ignored

    end = client.post("/session_manager/sessions.end", json=payload)
    assert end.status_code == 200, end.text
    data = end.json()

    # preserve original session_id
    assert data["session_id"] == session_id

    # new unique server record_id (not client; not reused from start)
    assert data["record_id"] != payload["record_id"]
    assert data["record_id"] != start_record_id
    uuid.UUID(data["record_id"])

    # server-authoritative timestamp (not client)
    assert data["timestamp"] != payload["timestamp"]
    assert data["timestamp"].endswith("Z")


def test_sessions_start_reject_active_session_no_side_effects_409(
    tmp_path, monkeypatch, client: TestClient
):
    import apps.schema_recorder.config as recorder_config
    import apps.session_manager.service as sm_service

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    user_id = "test_user"

    # First start succeeds (creates dir + appends 1 line + mutates _sessions)
    r1 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r1.status_code == 200, r1.text
    first = r1.json()
    first_session_id = first["session_id"]

    # Snapshot state + filesystem after first start
    assert list(sm_service._sessions.keys()) == [first_session_id]
    sessions_dir = recorder_config.LOG_ROOT / "users" / user_id / "sessions"
    assert sessions_dir.exists()
    log_path = sessions_dir / f"{first_session_id}.jsonl"
    before_log_text = log_path.read_text(encoding="utf-8")
    before_sessions_dir_listing = sorted(p.name for p in sessions_dir.iterdir())

    # Fail-fast: second start must reject BEFORE generating a new session_id
    monkeypatch.setattr(
        sm_service,
        "generate_session_id",
        lambda: (_ for _ in ()).throw(
            AssertionError("generate_session_id must not be called")
        ),
    )

    r2 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["detail"] == "User already has an active session"

    # No in-memory mutation
    assert list(sm_service._sessions.keys()) == [first_session_id]
    assert sm_service._sessions[first_session_id]["status"] == "active"

    # No mkdir / no new session file / no append
    assert sessions_dir.exists()
    after_sessions_dir_listing = sorted(p.name for p in sessions_dir.iterdir())
    assert after_sessions_dir_listing == before_sessions_dir_listing
    assert log_path.read_text(encoding="utf-8") == before_log_text


def test_sessions_end_append_failure_returns_500_and_session_remains_active(
    tmp_path, monkeypatch
):
    from fastapi.testclient import TestClient

    import apps.schema_recorder.config as recorder_config
    import apps.schema_recorder.repository as repo
    import apps.session_manager.service as sm_service
    from api.main import app

    recorder_config.LOG_ROOT = tmp_path / "logs"
    sm_service._sessions.clear()

    c = TestClient(app, raise_server_exceptions=False)

    start = c.post(
        "/session_manager/sessions.start", json=_start_payload(user_id="test_user")
    )
    assert start.status_code == 200, start.text
    s = start.json()
    sid = s["session_id"]

    # Force repository append failure (recorder path)
    monkeypatch.setattr(
        repo,
        "append_bytes",
        lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")),
    )

    r1 = c.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id="test_user", session_id=sid),
    )
    assert r1.status_code == 500, r1.text

    # Remove failure and end again; must succeed if session remained active
    monkeypatch.undo()

    r2 = c.post(
        "/session_manager/sessions.end",
        json=_end_payload(user_id="test_user", session_id=sid),
    )
    assert r2.status_code == 200, r2.text


def test_sessions_start_missing_performer_id_rejected_400(client: TestClient):
    payload = _start_payload()
    payload.pop("performer_id", None)  # omit required-at-ingress performer_id

    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 400, r.text
    assert "performer_id is required" in r.json()["detail"]


def test_sessions_end_missing_performer_id_rejected_400(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    s = start.json()
    session_id, user_id = s["session_id"], s["user_id"]

    payload = _end_payload(user_id=user_id, session_id=session_id)
    payload.pop("performer_id", None)  # omit

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 400, r.text
    assert "performer_id is required" in r.json()["detail"]


def test_sessions_start_allows_system_performer_id(client: TestClient):
    payload = _start_payload(performer_id="system")
    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["performer_id"] == "system"


def test_sessions_end_allows_system_performer_id(client: TestClient):
    start = client.post(
        "/session_manager/sessions.start",
        json=_start_payload(performer_id="tester"),
    )
    assert start.status_code == 200, start.text
    s = start.json()

    payload = _end_payload(user_id=s["user_id"], session_id=s["session_id"])
    payload["performer_id"] = "system"

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["performer_id"] == "system"


def test_sessions_start_empty_performer_id_rejected_400(client: TestClient):
    payload = _start_payload(performer_id="")
    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 400, r.text
    assert "performer_id is required" in r.json()["detail"]


def test_sessions_end_empty_performer_id_rejected_400(client: TestClient):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    s = start.json()

    payload = _end_payload(user_id=s["user_id"], session_id=s["session_id"])
    payload["performer_id"] = ""  # explicitly empty

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 400, r.text
    assert "performer_id is required" in r.json()["detail"]


def test_sessions_start_does_not_infer_performer_id_from_user_id(client: TestClient):
    payload = _start_payload()

    payload.pop("performer_id", None)

    r = client.post("/session_manager/sessions.start", json=payload)
    assert r.status_code == 400, r.text
    assert "performer_id is required" in r.json()["detail"]


def test_sessions_end_unknown_session_id_returns_404_not_found(client: TestClient):
    payload = _end_payload(
        user_id=str(uuid.uuid4()),
        session_id="sess_DOES_NOT_EXIST",
    )

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Session not found"


def test_sessions_end_existing_session_wrong_user_returns_403_forbidden(
    client: TestClient,
):
    start = client.post("/session_manager/sessions.start", json=_start_payload())
    assert start.status_code == 200, start.text
    sid = start.json()["session_id"]

    payload = _end_payload(
        user_id=str(uuid.uuid4()),  # wrong user
        session_id=sid,
    )

    r = client.post("/session_manager/sessions.end", json=payload)
    assert r.status_code == 403, r.text
    assert r.json()["detail"] == "Session user mismatch"


def test_sessions_start_already_active_returns_409_conflict(client: TestClient):
    user_id = str(uuid.uuid4())

    r1 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        "/session_manager/sessions.start", json=_start_payload(user_id=user_id)
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["detail"] == "User already has an active session"
