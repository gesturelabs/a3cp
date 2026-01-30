# apps/session_manager/service.py

from datetime import datetime, timezone
from uuid import uuid4

from apps.schema_recorder.service import MissingSessionPath, append_event
from apps.session_manager.idgen import generate_session_id
from schemas import (
    SessionManagerEndInput,
    SessionManagerEndOutput,
    SessionManagerStartInput,
    SessionManagerStartOutput,
)


class SessionError(ValueError):
    pass


class SessionAlreadyActive(SessionError):
    pass


class SessionNotFound(SessionError):
    pass


class SessionUserMismatch(SessionError):
    pass


class SessionAlreadyClosed(SessionError):
    pass


# Temporary in-memory store for sessions (demo-only)
_sessions: dict[str, dict] = {}


def _now_utc_z() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def start_session(payload: SessionManagerStartInput) -> SessionManagerStartOutput:
    pid = payload.performer_id
    if pid != "system" and (pid is None or str(pid).strip() == ""):
        raise SessionError(
            "performer_id is required (use 'system' for system-initiated boundaries)"
        )

    for s in _sessions.values():
        if s["user_id"] == payload.user_id and s.get("status") == "active":
            raise SessionAlreadyActive("User already has an active session")

    new_session_id = generate_session_id()
    while new_session_id in _sessions:
        new_session_id = generate_session_id()

    now = datetime.now(timezone.utc)

    is_training = (
        bool(payload.is_training_data)
        if payload.is_training_data is not None
        else False
    )

    out = SessionManagerStartOutput(
        schema_version=payload.schema_version,
        record_id=(uuid4()),  # server-authoritative
        user_id=payload.user_id,
        timestamp=now,
        performer_id=payload.performer_id,
        source="session_manager",
        session_id=new_session_id,
        start_time=now,
        is_training_data=is_training,
        session_notes=payload.session_notes,
        training_intent_label=payload.training_intent_label,
    )

    from apps.schema_recorder.config import LOG_ROOT

    sessions_dir = LOG_ROOT / "users" / str(out.user_id) / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    append_event(user_id=out.user_id, session_id=str(out.session_id), message=out)

    _sessions[new_session_id] = {
        "user_id": payload.user_id,
        "start_time": now,
        "is_training_data": is_training,
        "session_notes": payload.session_notes,
        "performer_id": payload.performer_id,
        "training_intent_label": payload.training_intent_label,
        "status": "active",
    }

    return out


def end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput:
    from apps.schema_recorder.config import LOG_ROOT

    pid = payload.performer_id
    if pid != "system" and (pid is None or str(pid).strip() == ""):
        raise SessionError(
            "performer_id is required (use 'system' for system-initiated boundaries)"
        )

    if not payload.session_id:
        raise SessionError("session_id is required")

    session_id = payload.session_id
    session = _sessions.get(session_id)

    if not session:
        raise SessionNotFound("Session not found")

    if session["user_id"] != payload.user_id:
        raise SessionUserMismatch("Session user mismatch")

    if session.get("status") == "closed":
        raise SessionAlreadyClosed("Session already closed")

    out = SessionManagerEndOutput(
        schema_version=payload.schema_version,
        record_id=uuid4(),
        user_id=payload.user_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        source="session_manager",
        performer_id=payload.performer_id,
        end_time=payload.end_time,
    )

    # Preflight: recorder requires parent sessions directory to exist
    sessions_dir = LOG_ROOT / "users" / str(out.user_id) / "sessions"
    if not sessions_dir.exists():
        raise MissingSessionPath(f"Missing parent session directory: {sessions_dir}")

    append_event(user_id=out.user_id, session_id=str(out.session_id), message=out)

    session["end_time"] = payload.end_time
    session["status"] = "closed"

    return out
