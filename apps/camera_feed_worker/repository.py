# apps/camera_feed_worker/repository.py

"""
camera_feed_worker.repository (Sprint 1)

In-memory state holder for camera_feed_worker.

Responsibilities (Sprint 1):
- Own mutable per-connection state (State machine state + per-connection metadata)
- Provide a minimal API to get/set/clear state
- Track per-connection correlation:
  - record_id uniqueness
  - capture_id stability
- No IO, no persistence, no logs

Sprint 1D (Forwarding boundary):
- Maintain bounded in-memory forward buffer per connection/capture
- No disk writes, no schema_recorder imports, no cross-app repository imports
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from apps.camera_feed_worker.service import IdleState, State

# ---------------------------------------------------------------------
# Forwarding boundary errors (repo-owned)
# ---------------------------------------------------------------------


class LimitForwardBufferExceeded(RuntimeError):
    pass


class ForwardFailed(RuntimeError):
    pass


class ForwardNotInitialized(RuntimeError):
    pass


class ForwardItemInvalid(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ForwardItem:
    # correlation
    capture_id: str
    seq: int
    timestamp_frame: datetime  # event-time from frame_meta

    # payload
    payload: (
        Any  # bytes | memoryview | bytearray (kept Any to avoid import-time coupling)
    )
    byte_length: int

    # context needed by adapter (avoid reading from domain again)
    encoding: str
    width: int
    height: int
    user_id: str
    session_id: str


# ---------------------------------------------------------------------
# Forwarding boundary types (repo-owned)
# ---------------------------------------------------------------------


class CameraFeedWorkerRepository:
    """
    Per-process in-memory repository.

    Keying:
    - Uses an opaque connection_key chosen by the route layer (e.g., a UUID).

    Concurrency:
    - Sprint 1 assumes a single event loop / single worker process for demo use.
    - If multiple workers are used later, this must be replaced with a shared store.
    """

    def __init__(self) -> None:
        self._records: Dict[str, dict] = {}

    def connection_keys(self) -> list[str]:
        return list(self._records.keys())

    def _ensure(self, connection_key: str) -> dict:
        if connection_key not in self._records:
            self._records[connection_key] = {
                # Sprint 1C
                "state": IdleState(),
                "seen_record_ids": set(),
                # Sprint 1D (forwarding boundary; JSON-only work may leave these unused)
                "forward_queue": None,  # asyncio.Queue[ForwardItem] | None
                "forward_frames": 0,
                "forward_bytes": 0,
                "forward_task": None,  # asyncio.Task | None
                "forward_error": None,  # <-- add here
                "max_forward_buffer_frames": None,
                "max_forward_buffer_bytes": None,
            }
        return self._records[connection_key]

    # ---------------------------------------------------------------------
    # State management
    # ---------------------------------------------------------------------

    def get_state(self, connection_key: str) -> State:
        return self._ensure(connection_key)["state"]

    def set_state(self, connection_key: str, state: State) -> None:
        self._ensure(connection_key)["state"] = state

    def reset_state(self, connection_key: str) -> None:
        self._ensure(connection_key)["state"] = IdleState()

    # ---------------------------------------------------------------------
    # record_id correlation (per connection)
    # ---------------------------------------------------------------------

    def has_seen_record_id(self, connection_key: str, record_id: str) -> bool:
        return record_id in self._ensure(connection_key)["seen_record_ids"]

    def mark_record_id_seen(self, connection_key: str, record_id: str) -> None:
        self._ensure(connection_key)["seen_record_ids"].add(record_id)

    # ---------------------------------------------------------------------
    # Forwarding boundary (Sprint 1D): API surface only (implementation next)
    # ---------------------------------------------------------------------

    def init_forwarding(
        self,
        connection_key: str,
        capture_id: str,
        *,
        max_frames: int,
        max_bytes: int,
    ) -> None:
        rec = self._ensure(connection_key)
        rec["forward_queue"] = asyncio.Queue()
        rec["forward_frames"] = 0
        rec["forward_bytes"] = 0
        rec["forward_task"] = None
        rec["max_forward_buffer_frames"] = int(max_frames)
        rec["max_forward_buffer_bytes"] = int(max_bytes)

    def get_forward_stats(self, connection_key: str) -> tuple[int, int]:
        rec = self._ensure(connection_key)
        return int(rec["forward_frames"]), int(rec["forward_bytes"])

    def start_forwarding_task(self, connection_key: str, task: asyncio.Task) -> None:
        rec = self._ensure(connection_key)
        rec["forward_task"] = task

        def _done(t: asyncio.Task) -> None:
            if t.cancelled():
                return
            exc = t.exception()
            if exc is not None:
                rec["forward_error"] = exc

        task.add_done_callback(_done)

    def raise_if_forward_failed(self, connection_key: str) -> None:
        rec = self._ensure(connection_key)
        err = rec.get("forward_error")
        if err is not None:
            raise ForwardFailed(f"downstream forward failed: {err}") from err

    def _validate_forward_item(self, item: object) -> "ForwardItem":
        if not isinstance(item, ForwardItem):
            raise ForwardItemInvalid("enqueue_frame expects ForwardItem")

        if not str(item.capture_id).strip():
            raise ForwardItemInvalid("ForwardItem.capture_id must be non-empty")

        if int(item.seq) < 1:
            raise ForwardItemInvalid("ForwardItem.seq must be >= 1")

        if not isinstance(item.timestamp_frame, datetime):
            raise ForwardItemInvalid("ForwardItem.timestamp_frame must be datetime")

        if not str(item.encoding).strip():
            raise ForwardItemInvalid("ForwardItem.encoding must be non-empty")

        if int(item.width) <= 0 or int(item.height) <= 0:
            raise ForwardItemInvalid("ForwardItem.width/height must be > 0")

        if not str(item.user_id).strip() or not str(item.session_id).strip():
            raise ForwardItemInvalid("ForwardItem.user_id/session_id must be non-empty")

        payload = item.payload
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            raise ForwardItemInvalid("ForwardItem.payload must be bytes-like")

        payload_len = len(payload)
        if int(item.byte_length) != int(payload_len):
            raise ForwardItemInvalid(
                f"ForwardItem.byte_length {item.byte_length} != len(payload) {payload_len}"
            )

        return item

    def _enforce_forward_buffer_bounds(
        self, rec: dict, item: "ForwardItem"
    ) -> tuple[int, int]:
        max_frames = int(rec["max_forward_buffer_frames"] or 0)
        max_bytes = int(rec["max_forward_buffer_bytes"] or 0)

        next_frames = int(rec["forward_frames"]) + 1
        next_bytes = int(rec["forward_bytes"]) + int(item.byte_length)

        if max_frames and next_frames > max_frames:
            raise LimitForwardBufferExceeded(
                f"forward buffer exceeded (frames={next_frames}/{max_frames}, bytes={next_bytes}/{max_bytes})"
            )
        if max_bytes and next_bytes > max_bytes:
            raise LimitForwardBufferExceeded(
                f"forward buffer exceeded (frames={next_frames}/{max_frames}, bytes={next_bytes}/{max_bytes})"
            )

        return next_frames, next_bytes

    def enqueue_frame(self, connection_key: str, item: "ForwardItem") -> None:
        rec = self._ensure(connection_key)
        q = rec["forward_queue"]
        if q is None:
            raise ForwardNotInitialized("forward_queue not initialized")

        # Locked repo invariants (ForwardItem validity)
        item = self._validate_forward_item(item)

        # Bounded buffer enforcement
        next_frames, next_bytes = self._enforce_forward_buffer_bounds(rec, item)

        q.put_nowait(item)
        rec["forward_frames"] = next_frames
        rec["forward_bytes"] = next_bytes

    async def dequeue_frame(self, connection_key: str) -> ForwardItem:
        """
        Await next ForwardItem and decrement buffer counters on removal.
        """
        rec = self._ensure(connection_key)
        q = rec["forward_queue"]
        if q is None:
            raise ForwardNotInitialized("forward_queue not initialized")

        item: ForwardItem = await q.get()

        rec["forward_frames"] = max(0, int(rec["forward_frames"]) - 1)
        rec["forward_bytes"] = max(0, int(rec["forward_bytes"]) - int(item.byte_length))
        return item

    def stop_forwarding(self, connection_key: str) -> None:
        rec = self._ensure(connection_key)

        task = rec.get("forward_task")
        if task is not None:
            task.cancel()
        rec["forward_task"] = None

        q = rec.get("forward_queue")
        if q is not None:
            while True:
                try:
                    item = q.get_nowait()
                except asyncio.QueueEmpty:
                    break
                rec["forward_frames"] = max(0, int(rec["forward_frames"]) - 1)
                rec["forward_bytes"] = max(
                    0,
                    int(rec["forward_bytes"]) - int(getattr(item, "byte_length", 0)),
                )

        rec["forward_queue"] = None
        rec["forward_frames"] = 0
        rec["forward_bytes"] = 0
        rec["max_forward_buffer_frames"] = None
        rec["max_forward_buffer_bytes"] = None
        rec["forward_error"] = None

    # ---------------------------------------------------------------------
    # Connection lifecycle
    # ---------------------------------------------------------------------

    def clear(self, connection_key: str) -> None:
        if connection_key in self._records:
            del self._records[connection_key]


# Default singleton repository instance (Sprint 1)
repo = CameraFeedWorkerRepository()
