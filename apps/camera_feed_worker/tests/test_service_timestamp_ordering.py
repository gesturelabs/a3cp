# apps/camera_feed_worker/tests/test_service_timestamp_ordering.py

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


class FrameMetaEvent:
    def __init__(self, *, seq: int, timestamp_frame: datetime, byte_length: int = 10):
        self.seq = seq
        self.timestamp_frame = timestamp_frame
        self.byte_length = byte_length


class CloseEvent:
    def __init__(self, *, timestamp_end: datetime):
        self.timestamp_end = timestamp_end


def _open_active(now_ingest: datetime) -> service.ActiveState:
    st, _ = service.dispatch(
        service.IdleState(), "capture.open", OpenEvent(), now_ingest
    )
    assert isinstance(st, service.ActiveState)
    return st


def _accept_one_frame(active: service.ActiveState) -> service.ActiveState:
    # meta at t=0.100s, bytes length 10, then bytes accepted
    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1,
            timestamp_frame=_dt("2026-02-04T12:00:00.100Z"),
            byte_length=10,
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)

    st2, _ = service.dispatch(
        st1,
        "capture.frame_bytes",
        10,
        _dt("2026-02-04T12:00:00.020Z"),
    )
    assert isinstance(st2, service.ActiveState)
    assert st2.last_frame_timestamp == _dt("2026-02-04T12:00:00.100Z")
    return st2


def test_timestamp_frame_less_than_last_frame_timestamp_aborts():
    active = _open_active(_dt("2026-02-04T12:00:00Z"))
    active = _accept_one_frame(active)

    # Next meta has timestamp earlier than last_frame_timestamp
    st2, actions = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=2,
            timestamp_frame=_dt("2026-02-04T12:00:00.090Z"),  # earlier than 0.100Z
            byte_length=10,
        ),
        _dt("2026-02-04T12:00:00.030Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)


def test_timestamp_end_less_than_timestamp_start_aborts():
    now_ingest = _dt("2026-02-04T12:00:00Z")

    # Open with event-time start at 12:00:10Z (future relative to end)
    st0, _ = service.dispatch(
        service.IdleState(),
        "capture.open",
        OpenEvent(timestamp_start=_dt("2026-02-04T12:00:10Z")),
        now_ingest,
    )
    assert isinstance(st0, service.ActiveState)

    st1, actions = service.dispatch(
        st0,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:09Z")),  # < start
        _dt("2026-02-04T12:00:09Z"),
    )

    assert isinstance(st1, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)


def test_timestamp_end_less_than_last_frame_timestamp_aborts():
    active = _open_active(_dt("2026-02-04T12:00:00Z"))
    active = _accept_one_frame(active)

    # Close with timestamp_end earlier than last_frame_timestamp (0.100Z)
    st2, actions = service.dispatch(
        active,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:00.090Z")),
        _dt("2026-02-04T12:00:00.090Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)
