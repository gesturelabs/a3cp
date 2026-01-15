# apps/schema_recorder/tests/test_routes.py

from __future__ import annotations

import re
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.schema_recorder.routes.router import router
from schemas import example_input

ISO8601_MS_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_invalid_schema_payload_rejected_422_and_service_not_called(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Patch where the router *uses* it (router imports the module object "service")
    mock_append = Mock()
    monkeypatch.setattr(
        "apps.schema_recorder.routes.router.service.append_event",
        mock_append,
        raising=True,
    )

    # Missing required BaseSchema fields: schema_version, record_id, user_id, timestamp
    resp = client.post("/schema-recorder/append", json={"nonsense": "payload"})

    assert resp.status_code == 422
    assert mock_append.call_count == 0


def test_unparseable_json_rejected_and_service_not_called(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_append = Mock()
    monkeypatch.setattr(
        "apps.schema_recorder.routes.router.service.append_event",
        mock_append,
        raising=True,
    )

    # Invalid JSON body (fails before Pydantic model validation)
    resp = client.post(
        "/schema-recorder/append",
        content=b'{"schema_version": "1.0.1",',  # truncated / invalid JSON
        headers={"Content-Type": "application/json"},
    )

    # Depending on FastAPI/Starlette version this is typically 400 for JSON decode error.
    # If your stack returns 422 instead, adjust this assertion accordingly.
    assert resp.status_code == 422
    assert mock_append.call_count == 0


@pytest.mark.parametrize("missing_field", ["user_id", "session_id", "source"])
def test_required_field_enforcement_422_and_no_service_call(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    missing_field: str,
) -> None:
    mock_append = Mock()
    monkeypatch.setattr(
        "apps.schema_recorder.routes.router.service.append_event",
        mock_append,
        raising=True,
    )

    payload = example_input()
    # Make payload valid for route checks by default
    payload["session_id"] = "session-001"
    payload["source"] = "gesture_classifier"

    payload.pop(missing_field)

    resp = client.post("/schema-recorder/append", json=payload)

    assert resp.status_code == 422
    assert mock_append.call_count == 0
    assert "detail" in resp.json()


@pytest.mark.parametrize(
    "exc, expected_status",
    [
        ("MissingSessionPath", 409),
        ("EventTooLarge", 413),
        ("RecorderIOError", 500),
    ],
)
def test_domain_exception_maps_to_http_status(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    exc: str,
    expected_status: int,
) -> None:
    # Import from the module used by the router, not deep schema paths.
    import apps.schema_recorder.service as service_module

    payload = example_input()
    payload["session_id"] = "session-001"
    payload["source"] = "gesture_classifier"

    message = f"{exc} simulated failure"
    exception_type = getattr(service_module, exc)

    def _raise(*args, **kwargs):
        raise exception_type(message)

    mock_append = Mock(side_effect=_raise)
    monkeypatch.setattr(
        "apps.schema_recorder.routes.router.service.append_event",
        mock_append,
        raising=True,
    )

    resp = client.post("/schema-recorder/append", json=payload)

    assert resp.status_code == expected_status
    assert mock_append.call_count == 1

    body = resp.json()
    assert body["detail"] == message


def test_success_contract_201_exact_keys_record_id_echo_and_recorded_at_shape(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import apps.schema_recorder.service as service_module

    payload = example_input()
    payload["session_id"] = "session-001"
    payload["source"] = "gesture_classifier"

    expected_record_id = payload["record_id"]
    expected_recorded_at = "2026-01-15T12:34:56.789Z"

    mock_append = Mock(
        return_value=service_module.AppendResult(
            record_id=expected_record_id,
            recorded_at=expected_recorded_at,
        )
    )
    monkeypatch.setattr(
        "apps.schema_recorder.routes.router.service.append_event",
        mock_append,
        raising=True,
    )

    resp = client.post("/schema-recorder/append", json=payload)

    assert resp.status_code == 201
    assert mock_append.call_count == 1

    body = resp.json()

    # exact contract: only these two keys
    assert set(body.keys()) == {"record_id", "recorded_at"}

    # record_id echoes request record_id
    assert body["record_id"] == expected_record_id

    # recorded_at is ISO-8601 ms with Z suffix (shape check only)
    assert isinstance(body["recorded_at"], str)
    assert ISO8601_MS_Z_RE.match(body["recorded_at"])
