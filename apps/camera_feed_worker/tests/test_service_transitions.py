# apps/camera_feed_worker/tests/test_service_transitions.py

from datetime import datetime

import pytest

from apps.camera_feed_worker import service


def _dt(s: str) -> datetime:
    # ISO8601 with Z
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class OpenEvent:
    def __init__(
        self,
        *,
        capture_id="cap-1",
        record_id="rec-1",
        user_id="user-1",
        session_id="sess-1",
        timestamp_start=None,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
    ):
        self.capture_id = capture_id
        self.record_id = record_id
        self.user_id = user_id
        self.session_id = session_id
        self.timestamp_start = timestamp_start or _dt("2026-02-04T12:00:00Z")
        self.fps_target = fps_target
        self.width = width
        self.height = height
        self.encoding = encoding


class CloseEvent:
    def __init__(self, *, timestamp_end=None):
        self.timestamp_end = timestamp_end or _dt("2026-02-04T12:00:01Z")


def test_capture_open_from_idle_to_active():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    state0 = service.IdleState()

    state1, actions = service.dispatch(state0, "capture.open", OpenEvent(), now_ingest)

    assert isinstance(state1, service.ActiveState)
    assert state1.kind == "active"
    assert any(isinstance(a, service.RequestSessionValidation) for a in actions)


def test_capture_open_from_active_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")

    # First open → active
    active_state, _ = service.dispatch(
        service.IdleState(), "capture.open", OpenEvent(), now_ingest
    )
    assert isinstance(active_state, service.ActiveState)

    # Second open while active → abort semantics
    state2, actions = service.dispatch(
        active_state, "capture.open", OpenEvent(), now_ingest
    )

    assert isinstance(state2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.capture_id == active_state.capture_id
    assert abort.error_code == "protocol_violation"


def test_capture_close_from_idle_raises_protocol_violation():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    with pytest.raises(service.ProtocolViolation):
        # In idle state, close is invalid and should raise (no abort wrapper)
        service.dispatch(service.IdleState(), "capture.close", CloseEvent(), now_ingest)


def test_unknown_event_kind_raises_protocol_violation_in_idle():
    now_ingest = _dt("2026-02-04T12:00:00Z")

    with pytest.raises(service.ProtocolViolation):
        service.dispatch(
            service.IdleState(),
            "capture.nope",  # type: ignore[arg-type]
            object(),
            now_ingest,
        )
