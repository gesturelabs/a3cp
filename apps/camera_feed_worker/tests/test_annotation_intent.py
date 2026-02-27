# apps/camera_feed_worker/tests/test_annotation_intent.py

import uuid
from datetime import datetime, timezone

from apps.camera_feed_worker.service import AbortCapture, dispatch
from apps.camera_feed_worker.state import ActiveState, IdleState
from schemas import CameraFeedWorkerInput


def _iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _open_msg(*, intent: str | None) -> dict:
    now = _iso_now()
    msg = {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": "u_test",
        "session_id": "sess_test",
        "timestamp": now,
        "modality": "image",
        "source": "ui",
        "event": "capture.open",
        "capture_id": str(uuid.uuid4()),
        "timestamp_start": now,
        "fps_target": 15,
        "width": 640,
        "height": 480,
        "encoding": "jpeg",
    }
    if intent is not None:
        msg["annotation"] = {"intent": intent}
    return msg


def _frame_meta_msg(*, capture_id: str, seq: int, byte_length: int) -> dict:
    now = _iso_now()
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": "u_test",
        "session_id": "sess_test",
        "timestamp": now,
        "modality": "image",
        "source": "ui",
        "event": "capture.frame_meta",
        "capture_id": capture_id,
        "seq": seq,
        "timestamp_frame": now,
        "byte_length": byte_length,
    }


def _close_msg(*, capture_id: str) -> dict:
    now = _iso_now()
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": "u_test",
        "session_id": "sess_test",
        "timestamp": now,
        "modality": "image",
        "source": "ui",
        "event": "capture.close",
        "capture_id": capture_id,
        "timestamp_end": now,
    }


def _assert_no_abort(actions) -> None:
    assert not any(isinstance(a, AbortCapture) for a in actions)


def test_dispatch_open_sets_annotation_intent() -> None:
    connection_key = f"ck_{uuid.uuid4()}"
    now_ingest = datetime.now(timezone.utc)

    msg = CameraFeedWorkerInput(**_open_msg(intent="wave"))
    current_state = IdleState()

    new_state, actions = dispatch(
        connection_key=connection_key,
        current_state=current_state,
        event_kind=msg.event,  # router uses msg.event for JSON control messages
        event=msg,
        now_ingest=now_ingest,
    )

    assert isinstance(new_state, ActiveState)
    assert new_state.annotation_intent == "wave"


def test_dispatch_open_without_annotation_sets_none() -> None:
    connection_key = f"ck_{uuid.uuid4()}"
    now_ingest = datetime.now(timezone.utc)

    msg = CameraFeedWorkerInput(**_open_msg(intent=None))
    current_state = IdleState()

    new_state, actions = dispatch(
        connection_key=connection_key,
        current_state=current_state,
        event_kind=msg.event,
        event=msg,
        now_ingest=now_ingest,
    )

    assert isinstance(new_state, ActiveState)
    assert new_state.annotation_intent is None


def test_success_path_emits_no_abort_and_returns_idle() -> None:
    """
    Deterministic replacement for:
      - Confirm no unexpected capture.abort

    Valid protocol sequence must not produce AbortCapture actions.
    """
    connection_key = f"ck_{uuid.uuid4()}"
    now_ingest = datetime.now(timezone.utc)

    # Use a stable capture_id so frame_meta/close correlate correctly.
    capture_id = f"cap_{uuid.uuid4()}"

    # 1) capture.open (with annotation is fine; could also omit)
    open_msg = {
        "schema_version": "1.0.1",
        "record_id": str(uuid.uuid4()),
        "user_id": "u_test",
        "session_id": "sess_test",
        "timestamp": _iso_now(),
        "modality": "image",
        "source": "ui",
        "event": "capture.open",
        "capture_id": capture_id,
        "timestamp_start": _iso_now(),
        "fps_target": 15,
        "width": 640,
        "height": 480,
        "encoding": "jpeg",
        "annotation": {"intent": "wave"},
    }
    msg_open = CameraFeedWorkerInput(**open_msg)

    state, actions = dispatch(
        connection_key=connection_key,
        current_state=IdleState(),
        event_kind=msg_open.event,
        event=msg_open,
        now_ingest=now_ingest,
    )
    _assert_no_abort(actions)
    assert isinstance(state, ActiveState)

    # 2) capture.frame_meta
    msg_meta = CameraFeedWorkerInput(
        **_frame_meta_msg(capture_id=capture_id, seq=1, byte_length=1234)
    )
    state2, actions2 = dispatch(
        connection_key=connection_key,
        current_state=state,
        event_kind=msg_meta.event,
        event=msg_meta,
        now_ingest=datetime.now(timezone.utc),
    )
    _assert_no_abort(actions2)

    # 3) capture.frame_bytes (router passes len(data_bytes) as event)
    state3, actions3 = dispatch(
        connection_key=connection_key,
        current_state=state2,
        event_kind="capture.frame_bytes",
        event=1234,
        now_ingest=datetime.now(timezone.utc),
    )
    _assert_no_abort(actions3)

    # 4) capture.close
    msg_close = CameraFeedWorkerInput(**_close_msg(capture_id=capture_id))
    state4, actions4 = dispatch(
        connection_key=connection_key,
        current_state=state3,
        event_kind=msg_close.event,
        event=msg_close,
        now_ingest=datetime.now(timezone.utc),
    )
    _assert_no_abort(actions4)
    assert isinstance(state4, IdleState)


def test_annotation_intent_cleared_on_close_via_idle_transition() -> None:
    """
    Deterministic replacement for:
      - Confirm server logs show correct annotation_intent in ActiveState
    by asserting the actual invariant:
      - intent exists only in ActiveState and is cleared when returning to IdleState.
    """
    connection_key = f"ck_{uuid.uuid4()}"
    capture_id = f"cap_{uuid.uuid4()}"

    msg_open = CameraFeedWorkerInput(
        **{
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": _iso_now(),
            "modality": "image",
            "source": "ui",
            "event": "capture.open",
            "capture_id": capture_id,
            "timestamp_start": _iso_now(),
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
            "annotation": {"intent": "hungry"},
        }
    )

    state, actions = dispatch(
        connection_key=connection_key,
        current_state=IdleState(),
        event_kind=msg_open.event,
        event=msg_open,
        now_ingest=datetime.now(timezone.utc),
    )
    _assert_no_abort(actions)
    assert isinstance(state, ActiveState)
    assert state.annotation_intent == "hungry"

    msg_close = CameraFeedWorkerInput(**_close_msg(capture_id=capture_id))
    state2, actions2 = dispatch(
        connection_key=connection_key,
        current_state=state,
        event_kind=msg_close.event,
        event=msg_close,
        now_ingest=datetime.now(timezone.utc),
    )
    _assert_no_abort(actions2)
    assert isinstance(state2, IdleState)
