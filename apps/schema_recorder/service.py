# apps/schema_recorder/service.py

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from schemas import BaseSchema


# -----------------------------
# Domain exceptions (service-level)
# -----------------------------
class MissingSessionPath(Exception):
    """Parent session directory does not exist (session_manager must create it)."""


class EventTooLarge(Exception):
    """Serialized JSONL line exceeds MAX_EVENT_BYTES."""


class RecorderIOError(Exception):
    """Any OS/FS-related failure during append (wrapped at repository boundary)."""


class PayloadNotAllowed(Exception):
    """Event contains transport payload fields that must not be persisted in JSONL logs."""


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
     Append one validated schema message to the session JSONL log for the given user/session.

    Inputs:
      - user_id: owner of the session log
      - session_id: target session identifier
      - message: validated BaseSchema instance (e.g. A3CPMessage)

    Behavior / guarantees:
      - resolves the session log path internally (callers do not pass paths)
      - wraps the payload as:
          { "recorded_at": <UTC ISO8601 ms Z>, "event": <message-as-received> }
      - enforces MAX_EVENT_BYTES over the UTF-8 bytes of the full JSONL line
      - raises only domain exceptions:
          MissingSessionPath, EventTooLarge, RecorderIOError
    """
    from apps.schema_recorder.config import LOG_ROOT
    from utils.paths import session_log_path

    log_path = session_log_path(
        log_root=LOG_ROOT, user_id=user_id, session_id=session_id
    )

    # Fail fast if session directory does not exist (recorder must not mkdir).

    recorded_at = _utc_now_iso8601_ms_z()

    # Dump once (do not serialize yet)
    event_dict = message.model_dump(mode="json")

    # ---- Payload rejection safety checks (MVP invariant) ----

    if _contains_key(event_dict, "frame_data"):
        raise PayloadNotAllowed(
            "Payload field 'frame_data' must not be recorded to JSONL"
        )

    if event_dict.get("audio_format") in ("base64", "bytes") and _contains_key(
        event_dict, "audio_payload"
    ):
        raise PayloadNotAllowed(
            "Payload field 'audio_payload' must not be recorded to JSONL"
        )

    if _contains_data_url_image(event_dict):
        raise PayloadNotAllowed("Data-URL image payloads must not be recorded to JSONL")

    # ----------------------------------------------------------

    envelope = {
        "recorded_at": recorded_at,
        "event": event_dict,
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


def _contains_key(obj: object, key: str) -> bool:
    if isinstance(obj, dict):
        if key in obj:
            return True
        return any(_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_key(v, key) for v in obj)
    return False


def _contains_data_url_image(obj: object) -> bool:
    if isinstance(obj, str):
        return obj.startswith("data:image/")
    if isinstance(obj, dict):
        return any(_contains_data_url_image(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_data_url_image(v) for v in obj)
    return False
