# apps/camera_feed_worker/state.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID


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
    record_id: UUID | None = None
    capture_id: str = ""
    user_id: str = ""
    session_id: str = ""

    # capture-time immutable annotation (Sprint 1)
    annotation_intent: str | None = None

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
