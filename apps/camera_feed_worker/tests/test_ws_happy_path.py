# apps/camera_feed_worker/tests/test_ws_happy_path.py

import json
import time  # add at top of file if not already present
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.session_manager import service as sm_service
from main import app


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# NEW (extended happy path: two frames, seq=1 and seq=2)


def test_ws_happy_path_end_to_end_two_frames_closes_cleanly_1000() -> None:
    """
    Given: active session, valid open/(meta+bytes)x2/close sequence
    Then: server does NOT emit capture.abort and closes normally (1000).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # frame 1 meta (arms binary gate)
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        # frame 1 bytes (disarms gate)
        ws.send_bytes(b"12345")

        # frame 2 meta (re-arms binary gate)
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 2,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        # frame 2 bytes (disarms gate again)
        ws.send_bytes(b"abcde")

        # close
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id,
                    "timestamp_end": _iso_now(),
                }
            )
        )

        msg = ws.receive()

        # If the server emitted capture.abort, it would be a text frame first.
        if msg.get("type") == "websocket.send":
            text = msg.get("text")
            assert isinstance(text, str), "Expected text payload in websocket.send"
            payload = json.loads(text)
            assert (
                payload.get("event") != "capture.abort"
            ), "Unexpected abort in happy path"

            # Next message must be close
            msg = ws.receive()

        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1000


# NEW (tick-interleaved happy path: inserts a pause to force at least one receive-timeout tick)


def test_ws_happy_path_end_to_end_two_frames_with_tick_interleaving_closes_cleanly_1000() -> (
    None
):
    """
    Given: active session, valid open/(meta+bytes)x2/close sequence
           with a short pause that forces at least one RECEIVE_TIMEOUT tick
    Then: server does NOT emit capture.abort and closes normally (1000).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # frame 1 meta (arms binary gate)
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        # frame 1 bytes (disarms gate)
        ws.send_bytes(b"12345")

        # Force at least one loop tick (RECEIVE_TIMEOUT_S=1.0), but stay safely under
        # META_TO_BYTES_TIMEOUT_S=2, IDLE_TIMEOUT_S=5, SESSION_RECHECK_INTERVAL_S=5.
        time.sleep(1.2)

        # frame 2 meta (re-arms binary gate)
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 2,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        # frame 2 bytes (disarms gate again)
        ws.send_bytes(b"abcde")

        # close
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id,
                    "timestamp_end": _iso_now(),
                }
            )
        )

        msg = ws.receive()

        if msg.get("type") == "websocket.send":
            text = msg.get("text")
            assert isinstance(text, str), "Expected text payload in websocket.send"
            payload = json.loads(text)
            assert (
                payload.get("event") != "capture.abort"
            ), "Unexpected abort in happy path"
            msg = ws.receive()

        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1000


def test_ws_happy_path_triggers_session_recheck_without_idle_timeout_closes_cleanly_1000() -> (
    None
):
    """
    Given: active session and an active capture
    When: we cross SESSION_RECHECK_INTERVAL_S (5s) but keep sending frame_meta within IDLE_TIMEOUT_S (5s)
    Then: server does NOT emit capture.abort and closes normally (1000).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # frame 1
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        ws.send_bytes(b"12345")

        # Sleep < IDLE_TIMEOUT_S so we don't trigger idle timeout...
        time.sleep(4.2)

        # ...then send another frame to refresh last_meta_ingest_timestamp
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 2,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )
        ws.send_bytes(b"abcde")

        # Now cross 5s since open; this forces RequestSessionRecheck on a tick,
        # but we stay safely under idle timeout because meta was recent.
        time.sleep(1.2)

        # close
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id,
                    "timestamp_end": _iso_now(),
                }
            )
        )

        msg = ws.receive()

        # If the server emitted capture.abort, it would be a text frame first.
        if msg.get("type") == "websocket.send":
            text = msg.get("text")
            assert isinstance(text, str), "Expected text payload in websocket.send"
            payload = json.loads(text)
            assert (
                payload.get("event") != "capture.abort"
            ), "Unexpected abort during session re-check"
            msg = ws.receive()

        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1000
