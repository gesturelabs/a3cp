# apps/camera_feed_worker/service.py

"""
camera_feed_worker.service (Sprint 1)

Pure domain logic only:
- State machine (idle/active)
- Limit enforcement
- Timestamp rules
- Typed domain errors (transport-agnostic)
- Action emission

No IO. No persistence. No WebSocket close codes. No JSON parsing.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Literal

# =============================================================================
# Sprint 1 locked limits
# =============================================================================

MAX_DURATION_S = 15
MAX_FPS = 15
MAX_WIDTH = 640
MAX_HEIGHT = 480
MAX_PIXELS = 307_200
MAX_FRAMES = 225
MAX_FRAME_BYTES = 300_000
MAX_TOTAL_BYTES = 50_000_000

# Timeouts / intervals (Sprint 1)
META_TO_BYTES_TIMEOUT_S = 2
IDLE_TIMEOUT_S = 5
SESSION_RECHECK_INTERVAL_S = 5


# =============================================================================
# Domain Errors (transport-agnostic)
# =============================================================================


class CameraFeedWorkerError(ValueError):
    error_code: str = "unknown_error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__class__.__name__)


# Protocol
class ProtocolViolation(CameraFeedWorkerError):
    error_code = "protocol_violation"


# Limits
class LimitDurationExceeded(CameraFeedWorkerError):
    error_code = "limit_duration_exceeded"


class LimitFrameCountExceeded(CameraFeedWorkerError):
    error_code = "limit_frame_count_exceeded"


class LimitResolutionExceeded(CameraFeedWorkerError):
    error_code = "limit_resolution_exceeded"


class LimitFpsExceeded(CameraFeedWorkerError):
    error_code = "limit_fps_exceeded"


class LimitFrameBytesExceeded(CameraFeedWorkerError):
    error_code = "limit_frame_bytes_exceeded"


class LimitTotalBytesExceeded(CameraFeedWorkerError):
    error_code = "limit_total_bytes_exceeded"


class LimitForwardBufferExceeded(CameraFeedWorkerError):
    error_code = "limit_forward_buffer_exceeded"


# Forwarding
class ForwardFailed(CameraFeedWorkerError):
    error_code = "forward_failed"


# Session
class SessionInvalid(CameraFeedWorkerError):
    error_code = "session_invalid"


class SessionClosed(CameraFeedWorkerError):
    error_code = "session_closed"


# =============================================================================
# State data
# =============================================================================


@dataclass(frozen=True)
class PendingMeta:
    seq: int
    timestamp_frame: datetime  # event-time
    byte_length: int
    meta_ingest_timestamp: datetime  # server ingest-time


@dataclass(frozen=True)
class IdleState:
    kind: Literal["idle"] = "idle"


@dataclass(frozen=True)
class ActiveState:
    kind: Literal["active"] = "active"

    # identifiers
    record_id: str = ""
    capture_id: str = ""
    user_id: str = ""
    session_id: str = ""

    # event-time
    timestamp_start: datetime | None = None
    last_frame_timestamp: datetime | None = None

    # ingest-time
    ingest_timestamp_open: datetime | None = None

    # params
    fps_target: int = 0
    width: int = 0
    height: int = 0
    encoding: str = "jpeg"

    # counters
    frame_count: int = 0
    total_bytes: int = 0
    expected_next_seq: int = 1

    # meta
    pending_meta: PendingMeta | None = None

    # ingest-time bookkeeping for tick rules
    last_meta_ingest_timestamp: datetime | None = None
    last_session_check_ingest_timestamp: datetime | None = None


State = IdleState | ActiveState


# =============================================================================
# Actions (service emits; route layer performs IO)
# =============================================================================


@dataclass(frozen=True)
class AbortCapture:
    error_code: str
    capture_id: str


@dataclass(frozen=True)
class ForwardFrame:
    capture_id: str
    seq: int
    timestamp_event: datetime
    byte_length: int


@dataclass(frozen=True)
class RequestSessionValidation:
    user_id: str
    session_id: str


@dataclass(frozen=True)
class RequestSessionRecheck:
    user_id: str
    session_id: str


@dataclass(frozen=True)
class CleanupCapture:
    capture_id: str


Action = (
    AbortCapture
    | ForwardFrame
    | RequestSessionValidation
    | RequestSessionRecheck
    | CleanupCapture
)


# =============================================================================
# Events (expected attributes)
# =============================================================================
# This service is transport-agnostic. It assumes `event` objects carry needed fields.
# Your route layer can pass your Pydantic schema instances directly (duck-typed).


def _get(event: Any, name: str) -> Any:
    if not hasattr(event, name):
        raise ProtocolViolation(f"Missing required field: {name}")
    return getattr(event, name)


# =============================================================================
# Helpers
# =============================================================================


def _seconds_since(now: datetime, then: datetime) -> float:
    return (now - then).total_seconds()


def _enforce_open_limits(*, fps_target: int, width: int, height: int) -> None:
    if fps_target > MAX_FPS:
        raise LimitFpsExceeded(f"fps_target {fps_target} exceeds max_fps {MAX_FPS}")
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise LimitResolutionExceeded(
            f"resolution {width}x{height} exceeds max {MAX_WIDTH}x{MAX_HEIGHT}"
        )
    if width * height > MAX_PIXELS:
        raise LimitResolutionExceeded(
            f"pixels {width*height} exceeds max_pixels {MAX_PIXELS}"
        )


def _require_active(state: State) -> ActiveState:
    if not isinstance(state, ActiveState) or state.kind != "active":
        raise ProtocolViolation("Expected active state")
    return state


def _require_idle(state: State) -> IdleState:
    if not isinstance(state, IdleState) or state.kind != "idle":
        raise ProtocolViolation("Expected idle state")
    return state


# =============================================================================
# Handlers (pure)
# =============================================================================


def handle_open(
    current_state: State, open_event: Any, now_ingest: datetime
) -> tuple[State, list[Action]]:
    _require_idle(current_state)

    # Required open fields (duck-typed):
    # capture_id, user_id, session_id, timestamp_start, fps_target, width, height, encoding(optional)
    capture_id = _get(open_event, "capture_id")
    user_id = _get(open_event, "user_id")
    session_id = _get(open_event, "session_id")
    timestamp_start = _get(open_event, "timestamp_start")
    fps_target = _get(open_event, "fps_target")
    width = _get(open_event, "width")
    height = _get(open_event, "height")
    encoding = getattr(open_event, "encoding", "jpeg")

    _enforce_open_limits(
        fps_target=int(fps_target), width=int(width), height=int(height)
    )

    new_state = ActiveState(
        record_id=str(_get(open_event, "record_id")),
        capture_id=str(capture_id),
        user_id=str(user_id),
        session_id=str(session_id),
        timestamp_start=timestamp_start,
        ingest_timestamp_open=now_ingest,
        fps_target=int(fps_target),
        width=int(width),
        height=int(height),
        encoding=str(encoding),
        frame_count=0,
        total_bytes=0,
        expected_next_seq=1,
        last_frame_timestamp=None,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )

    actions: list[Action] = [
        RequestSessionValidation(user_id=str(user_id), session_id=str(session_id))
    ]
    return new_state, actions


def handle_frame_meta(
    current_state: State, meta_event: Any, now_ingest: datetime
) -> tuple[State, list[Action]]:
    s = _require_active(current_state)

    if s.pending_meta is not None:
        raise ProtocolViolation(
            "pending_meta already set; frame_meta must not arrive twice"
        )

    seq = int(_get(meta_event, "seq"))
    timestamp_frame: datetime = _get(meta_event, "timestamp_frame")
    byte_length = int(_get(meta_event, "byte_length"))

    if seq != s.expected_next_seq:
        raise ProtocolViolation(f"seq {seq} != expected_next_seq {s.expected_next_seq}")

    if s.last_frame_timestamp is not None and timestamp_frame < s.last_frame_timestamp:
        raise ProtocolViolation("timestamp_frame must be >= last_frame_timestamp")

    pending = PendingMeta(
        seq=seq,
        timestamp_frame=timestamp_frame,
        byte_length=byte_length,
        meta_ingest_timestamp=now_ingest,
    )

    new_state = replace(
        s,
        pending_meta=pending,
        last_meta_ingest_timestamp=now_ingest,
    )
    return new_state, []


def handle_frame_bytes(
    current_state: State, byte_length: int, now_ingest: datetime
) -> tuple[State, list[Action]]:
    s = _require_active(current_state)

    if s.pending_meta is None:
        raise ProtocolViolation("frame_bytes received without pending_meta")

    pm = s.pending_meta

    # Invariant: received_byte_length == pending_meta.byte_length
    if int(byte_length) != int(pm.byte_length):
        raise ProtocolViolation(
            f"received_byte_length {byte_length} != pending_meta.byte_length {pm.byte_length}"
        )

    if byte_length > MAX_FRAME_BYTES:
        raise LimitFrameBytesExceeded(
            f"frame_bytes {pm.byte_length} exceeds max_frame_bytes {MAX_FRAME_BYTES}"
        )

    if s.total_bytes + byte_length > MAX_TOTAL_BYTES:
        raise LimitTotalBytesExceeded("total_bytes would exceed max_total_bytes")

    if s.frame_count + 1 > MAX_FRAMES:
        raise LimitFrameCountExceeded("frame_count would exceed max_frames")

    # Accept frame (only now increment counters)
    new_state = replace(
        s,
        frame_count=s.frame_count + 1,
        total_bytes=s.total_bytes + pm.byte_length,
        last_frame_timestamp=pm.timestamp_frame,
        expected_next_seq=s.expected_next_seq + 1,
        pending_meta=None,
    )

    actions: list[Action] = [
        ForwardFrame(
            capture_id=s.capture_id,
            seq=pm.seq,
            timestamp_event=pm.timestamp_frame,
            byte_length=pm.byte_length,
        )
    ]
    return new_state, actions


def handle_close(
    current_state: State, close_event: Any, now_ingest: datetime
) -> tuple[State, list[Action]]:
    s = _require_active(current_state)

    if s.pending_meta is not None:
        raise ProtocolViolation("pending_meta must be None for capture.close")

    timestamp_end: datetime = _get(close_event, "timestamp_end")

    if s.timestamp_start is None:
        raise ProtocolViolation("timestamp_start missing in active state")

    if timestamp_end < s.timestamp_start:
        raise ProtocolViolation("timestamp_end must be >= timestamp_start")

    if s.last_frame_timestamp is not None and timestamp_end < s.last_frame_timestamp:
        raise ProtocolViolation("timestamp_end must be >= last_frame_timestamp")

    # Event-time validation on close
    if (timestamp_end - s.timestamp_start).total_seconds() > MAX_DURATION_S:
        raise LimitDurationExceeded("event-time duration exceeds max_duration_s")

    # Success close → cleanup and return to idle
    return IdleState(), [CleanupCapture(capture_id=s.capture_id)]


def handle_tick(
    current_state: State, now_ingest: datetime
) -> tuple[State, list[Action]]:
    if isinstance(current_state, IdleState):
        return current_state, []

    s = _require_active(current_state)

    if s.ingest_timestamp_open is None:
        raise ProtocolViolation("ingest_timestamp_open missing in active state")

    # 1) Ingest-time duration guard (during capture)
    if _seconds_since(now_ingest, s.ingest_timestamp_open) > MAX_DURATION_S:
        raise LimitDurationExceeded("ingest-time duration exceeds max_duration_s")

    # 2) Meta→bytes timeout
    if s.pending_meta is not None:
        if (
            _seconds_since(now_ingest, s.pending_meta.meta_ingest_timestamp)
            > META_TO_BYTES_TIMEOUT_S
        ):
            raise ProtocolViolation("meta→bytes timeout exceeded")

    # 3) Idle timeout (no frame_meta for 5s while active)
    if s.last_meta_ingest_timestamp is not None:
        if _seconds_since(now_ingest, s.last_meta_ingest_timestamp) > IDLE_TIMEOUT_S:
            raise ProtocolViolation("idle timeout exceeded (no frame_meta)")

    # 4) Session re-check trigger
    actions: list[Action] = []
    if s.last_session_check_ingest_timestamp is None:
        # Defensive: treat as due
        actions.append(
            RequestSessionRecheck(user_id=s.user_id, session_id=s.session_id)
        )
        new_state = replace(s, last_session_check_ingest_timestamp=now_ingest)
        return new_state, actions

    if (
        _seconds_since(now_ingest, s.last_session_check_ingest_timestamp)
        >= SESSION_RECHECK_INTERVAL_S
    ):
        actions.append(
            RequestSessionRecheck(user_id=s.user_id, session_id=s.session_id)
        )
        s = replace(s, last_session_check_ingest_timestamp=now_ingest)

    return s, actions


# =============================================================================
# Dispatcher with Abort Semantics (per spec)
# =============================================================================

EventKind = Literal[
    "capture.open", "capture.frame_meta", "capture.frame_bytes", "capture.close", "tick"
]


def dispatch(
    current_state: State, event_kind: EventKind, event: Any, now_ingest: datetime
) -> tuple[State, list[Action]]:
    """
    Single entry point that applies Sprint 1 abort semantics.

    - Calls the corresponding handler.
    - If a CameraFeedWorkerError is raised while in ActiveState:
        emits AbortCapture(error_code, capture_id) + CleanupCapture(capture_id),
        returns IdleState.
    - If error occurs in IdleState:
        re-raises (protocol violation).
    """
    try:
        if event_kind == "capture.open":
            return handle_open(current_state, event, now_ingest)
        if event_kind == "capture.frame_meta":
            return handle_frame_meta(current_state, event, now_ingest)
        if event_kind == "capture.frame_bytes":
            # event is expected to be an int byte_length or have byte_length attr
            byte_len = int(
                event if isinstance(event, int) else _get(event, "byte_length")
            )
            return handle_frame_bytes(current_state, byte_len, now_ingest)
        if event_kind == "capture.close":
            return handle_close(current_state, event, now_ingest)
        if event_kind == "tick":
            return handle_tick(current_state, now_ingest)

        raise ProtocolViolation(f"Unknown event_kind: {event_kind}")

    except CameraFeedWorkerError as e:
        if isinstance(current_state, ActiveState):
            capture_id = current_state.capture_id
            actions: list[Action] = [
                AbortCapture(error_code=e.error_code, capture_id=capture_id),
                CleanupCapture(capture_id=capture_id),
            ]
            return IdleState(), actions
        raise

    except Exception as e:
        # Convert unexpected errors into typed domain error
        if isinstance(current_state, ActiveState):
            capture_id = current_state.capture_id
            actions: list[Action] = [
                AbortCapture(error_code="protocol_violation", capture_id=capture_id),
                CleanupCapture(capture_id=capture_id),
            ]
            return IdleState(), actions
        raise ProtocolViolation(str(e)) from e
