# apps/camera_feed_worker/tests/test_ws_forward_failure.py

import json
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.main import app
from apps.camera_feed_worker.repository import ForwardFailed
from apps.camera_feed_worker.routes import router as cfw_router_mod
from apps.camera_feed_worker.service import ActiveState


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.mark.integration
def test_ws_emits_abort_on_forward_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Deterministic Step 6.9 test (forward failure):
    Trigger forward failure only after capture.open transitions to ActiveState,
    and do NOT send frames so we hit the loop-level forward failure handler
    (which must emit capture.abort(error_code=forward_failed) then close).
    """

    # 1) Make session validation always succeed (avoid coupling to session store)
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    # 2) Raise ForwardFailed only once the repo state is ActiveState
    def _raise_if_forward_failed(connection_key: str) -> None:
        state = cfw_router_mod.repo.get_state(connection_key)
        if isinstance(state, ActiveState):
            raise ForwardFailed("forced forward failure for test")

    monkeypatch.setattr(
        cfw_router_mod.repo, "raise_if_forward_failed", _raise_if_forward_failed
    )

    client = TestClient(app)

    with client.websocket_connect("/camera_feed_worker/capture") as ws:
        now = _iso_now()
        capture_id = str(uuid.uuid4())

        open_msg = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": now,
            "modality": "image",
            "source": "ui",
            "event": "capture.open",
            "capture_id": capture_id,
            "timestamp_start": now,
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }

        ws.send_text(json.dumps(open_msg))

        # Do not send any frames. The WS loop ticks; on the next iteration
        # loop-level raise_if_forward_failed() should emit capture.abort then close.
        msg = json.loads(ws.receive_text())
        assert msg["event"] == "capture.abort"
        assert msg["error_code"] == "forward_failed"
        assert msg["capture_id"] == capture_id

        # After abort, server closes; next read should disconnect (code may be 1000)
        with pytest.raises(WebSocketDisconnect):
            ws.receive_text()


def test_ws_emits_abort_on_forward_failed_during_binary_phase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Forward failure while expecting binary must emit capture.abort(error_code=forward_failed)
    and close cleanly (1000), not 1011.
    """
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    calls = {"n": 0}

    def _raise_if_forward_failed(_: str) -> None:
        calls["n"] += 1
        # Ensure we get past capture.open; raise when handling the binary frame.
        if calls["n"] >= 3:
            raise ForwardFailed("forced forward failure (binary phase)")

    monkeypatch.setattr(
        cfw_router_mod.repo, "raise_if_forward_failed", _raise_if_forward_failed
    )

    client = TestClient(app)

    with client.websocket_connect("/camera_feed_worker/capture") as ws:
        now = _iso_now()
        capture_id = str(uuid.uuid4())

        open_msg = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": now,
            "modality": "image",
            "source": "ui",
            "event": "capture.open",
            "capture_id": capture_id,
            "timestamp_start": now,
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }
        ws.send_text(json.dumps(open_msg))

        # Arm binary gate
        now2 = _iso_now()
        payload = b"\x00"
        meta = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": now2,
            "modality": "image",
            "source": "ui",
            "event": "capture.frame_meta",
            "capture_id": capture_id,
            "seq": 1,
            "timestamp_frame": now2,
            "byte_length": len(payload),
        }
        ws.send_text(json.dumps(meta))
        ws.send_bytes(payload)

        # Must receive abort (unified semantics)
        abort = json.loads(ws.receive_text())
        assert abort["event"] == "capture.abort"
        assert abort["error_code"] == "forward_failed"
        assert abort["capture_id"] == capture_id

        with pytest.raises(WebSocketDisconnect):
            ws.receive_text()


def test_ws_forward_failed_fallback_closes_1011_when_abort_not_constructible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    If forward failure occurs before any valid control message is processed
    (so last_msg_for_emit is None), the server cannot construct capture.abort
    and must fall back to closing with 1011.
    """
    # Session validation irrelevant here, but keep deterministic.
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    # Raise immediately on first loop iteration (before any message parsed),
    # ensuring last_msg_for_emit is still None.
    def _raise_if_forward_failed(_: str) -> None:
        raise ForwardFailed("forced forward failure before any control message")

    monkeypatch.setattr(
        cfw_router_mod.repo, "raise_if_forward_failed", _raise_if_forward_failed
    )

    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)

    with client.websocket_connect("/camera_feed_worker/capture") as ws:
        # Server should close quickly; any receive should disconnect.
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()

        # Prefer asserting close code if available in this Starlette version.
        code = getattr(exc.value, "code", None)
        if code is not None:
            assert code == 1011
