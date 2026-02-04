# apps/camera_feed_worker/tests/test_service_duration_enforcement.py

from datetime import datetime

from apps.camera_feed_worker import service


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class OpenEvent:
    def __init__(
        self,
        *,
        capture_id="cap-1",
        user_id="user-1",
        session_id="sess-1",
        timestamp_start=None,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
    ):
        self.capture_id = capture_id
        self.user_id = user_id
        self.session_id = session_id
        self.timestamp_start = timestamp_start or _dt("2026-02-04T12:00:00Z")
        self.fps_target = fps_target
        self.width = width
        self.height = height
        self.encoding = encoding


class CloseEvent:
    def __init__(self, *, timestamp_end: datetime):
        self.timestamp_end = timestamp_end


def _open_active(
    now_ingest: datetime, *, timestamp_start: datetime | None = None
) -> service.ActiveState:
    ev = OpenEvent(timestamp_start=timestamp_start) if timestamp_start else OpenEvent()
    st, _ = service.dispatch(service.IdleState(), "capture.open", ev, now_ingest)
    assert isinstance(st, service.ActiveState)
    return st


def test_ingest_time_duration_exceeded_during_tick_aborts():
    # Open at ingest-time 12:00:00Z
    active = _open_active(_dt("2026-02-04T12:00:00Z"))

    # Tick after >15s
    st2, actions = service.dispatch(
        active,
        "tick",
        object(),
        _dt("2026-02-04T12:00:16Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "limit_duration_exceeded"


def test_event_time_duration_exceeded_on_close_aborts():
    # Event-time start at 12:00:00Z
    active = _open_active(
        now_ingest=_dt("2026-02-04T12:00:00Z"),
        timestamp_start=_dt("2026-02-04T12:00:00Z"),
    )

    # Close with event-time end at 12:00:16Z (>15s)
    st2, actions = service.dispatch(
        active,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:16Z")),
        _dt("2026-02-04T12:00:16Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "limit_duration_exceeded"


def test_valid_duration_close_returns_idle_and_cleanup():
    active = _open_active(
        now_ingest=_dt("2026-02-04T12:00:00Z"),
        timestamp_start=_dt("2026-02-04T12:00:00Z"),
    )

    st2, actions = service.dispatch(
        active,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:05Z")),
        _dt("2026-02-04T12:00:05Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)
    assert not any(isinstance(a, service.AbortCapture) for a in actions)
