# apps/schema_recorder/service.py

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from schemas.base.base import BaseSchema


# -----------------------------
# Domain exceptions (service-level)
# -----------------------------
class MissingSessionPath(Exception):
    """Parent session directory does not exist (session_manager must create it)."""


class EventTooLarge(Exception):
    """Serialized JSONL line exceeds MAX_EVENT_BYTES."""


class RecorderIOError(Exception):
    """Any OS/FS-related failure during append (wrapped at repository boundary)."""


# -----------------------------
# Service config (MVP)
# -----------------------------
# NOTE: Keep this constant here for MVP. You can move it to apps/schema_recorder/config.py later.
MAX_EVENT_BYTES: int = 512 * 1024  # 512 KiB per JSONL line (including newline)


@dataclass(frozen=True)
class AppendResult:
    record_id: str
    recorded_at: str


# -----------------------------
# Public service API (MVP)
# -----------------------------
def append_event(*, user_id: str, session_id: str, message: BaseSchema) -> AppendResult:
    """
    Append one event to the session JSONL log at `log_path`.

    Inputs:
      - log_path: fully resolved path (routes compute via utils/paths.py)
      - event: validated A3CPMessage (routes enforce required session_id/source)

    Guarantees:
      - wraps as { "recorded_at": <UTC ISO8601 ms Z>, "event": <event-as-received> }
      - enforces MAX_EVENT_BYTES over the UTF-8 bytes of the full JSONL line
      - raises ONLY domain exceptions (MissingSessionPath, EventTooLarge, RecorderIOError)
    """
    from apps.schema_recorder.config import LOG_ROOT
    from utils.paths import session_log_path

    log_path = session_log_path(
        log_root=LOG_ROOT, user_id=user_id, session_id=session_id
    )

    # Fail fast if session directory does not exist (recorder must not mkdir).

    recorded_at = _utc_now_iso8601_ms_z()

    # Preserve event "exactly as received": serialize from the pydantic object without mutation.
    # (This assumes A3CPMessage itself was the validated request payload.)
    envelope = {
        "recorded_at": recorded_at,
        "event": message.model_dump(mode="json"),
    }

    # Serialize to exactly one JSON line + newline.
    # ensure_ascii=False preserves unicode; separators minimizes bytes while remaining valid JSON.
    line = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")) + "\n"
    line_bytes = line.encode("utf-8")

    if len(line_bytes) > MAX_EVENT_BYTES:
        raise EventTooLarge(
            f"Event bytes {len(line_bytes)} exceed MAX_EVENT_BYTES={MAX_EVENT_BYTES}"
        )

    # Delegate IO to repository boundary (implemented next step).
    try:
        import apps.schema_recorder.repository as repository

        repository.append_bytes(log_path=log_path, line_bytes=line_bytes)
    except (MissingSessionPath, EventTooLarge, RecorderIOError):
        # Allow domain exceptions to pass through unchanged.
        raise
    except OSError as e:
        # If repository leaks raw OS errors, normalize here.
        raise RecorderIOError(str(e)) from e
    except Exception as e:
        # Any unexpected failure becomes RecorderIOError at the service boundary.
        raise RecorderIOError(str(e)) from e

    return AppendResult(record_id=str(message.record_id), recorded_at=recorded_at)


# -----------------------------
# Helpers (pure)
# -----------------------------
def _utc_now_iso8601_ms_z() -> str:
    # UTC, ISO 8601, millisecond precision, Z suffix
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
