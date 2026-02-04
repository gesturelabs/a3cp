# apps/camera_feed_worker/tests/test_service_protocol_sequencing.py

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
    def __init__(self, *, seq: int, timestamp_frame=None, byte_length: int = 10):
        self.seq = seq
        self.timestamp_frame = timestamp_frame or _dt("2026-02-04T12:00:00.100Z")
        self.byte_length = byte_length


class CloseEvent:
    def __init__(self, *, timestamp_end=None):
        self.timestamp_end = timestamp_end or _dt("2026-02-04T12:00:01Z")


def _open_active(now_ingest: datetime) -> service.ActiveState:
    st, _ = service.dispatch(
        service.IdleState(), "capture.open", OpenEvent(), now_ingest
    )
    assert isinstance(st, service.ActiveState)
    return st


def test_frame_meta_correct_seq_accepted():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    st2, actions = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=1, byte_length=123),
        _dt("2026-02-04T12:00:00.010Z"),
    )

    assert isinstance(st2, service.ActiveState)
    assert st2.pending_meta is not None
    assert st2.pending_meta.seq == 1
    assert st2.pending_meta.byte_length == 123
    assert actions == []


def test_frame_meta_wrong_seq_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    st2, actions = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=2, byte_length=10),
        _dt("2026-02-04T12:00:00.010Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.capture_id == active.capture_id
    assert abort.error_code == "protocol_violation"


def test_frame_meta_when_pending_meta_exists_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    # First meta sets pending_meta
    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=1, byte_length=10),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)
    assert st1.pending_meta is not None

    # Second meta without bytes should abort
    st2, actions = service.dispatch(
        st1,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, byte_length=10
        ),  # seq doesn't matter; pending_meta violation first
        _dt("2026-02-04T12:00:00.020Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)


def test_frame_bytes_without_pending_meta_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    st2, actions = service.dispatch(
        active,
        "capture.frame_bytes",
        10,  # byte_length
        _dt("2026-02-04T12:00:00.010Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)


def test_frame_bytes_mismatched_byte_length_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=1, byte_length=100),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)
    assert st1.pending_meta is not None

    st2, actions = service.dispatch(
        st1,
        "capture.frame_bytes",
        99,  # mismatch
        _dt("2026-02-04T12:00:00.020Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "protocol_violation"


def test_capture_close_with_pending_meta_present_aborts_and_cleans_up():
    now_ingest = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now_ingest)

    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=1, byte_length=10),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)
    assert st1.pending_meta is not None

    st2, actions = service.dispatch(
        st1,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:01Z")),
        _dt("2026-02-04T12:00:01Z"),
    )

    assert isinstance(st2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)
