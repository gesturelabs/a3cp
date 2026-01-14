# apps/session_manager/service.py


from datetime import datetime, timezone

from apps.schema_recorder.service import append_event
from apps.session_manager.idgen import generate_session_id
from schemas import (
    SessionManagerEndInput,
    SessionManagerEndOutput,
    SessionManagerStartInput,
    SessionManagerStartOutput,
)


class SessionError(ValueError):
    pass


class SessionNotFound(SessionError):
    pass


# Temporary in-memory store for sessions (demo-only)
_sessions: dict[str, dict] = {}


def start_session(payload: SessionManagerStartInput) -> SessionManagerStartOutput:
    new_session_id = generate_session_id()
    while new_session_id in _sessions:
        new_session_id = generate_session_id()

    now = datetime.now(timezone.utc)

    is_training = (
        bool(payload.is_training_data)
        if payload.is_training_data is not None
        else False
    )

    _sessions[new_session_id] = {
        "user_id": payload.user_id,
        "start_time": now,
        "is_training_data": is_training,
        "session_notes": payload.session_notes,
        "performer_id": payload.performer_id,
        "training_intent_label": payload.training_intent_label,
        "status": "active",
    }

    out = SessionManagerStartOutput(
        schema_version=payload.schema_version,
        record_id=payload.record_id,
        user_id=payload.user_id,
        timestamp=now,  # server acknowledgement time
        performer_id=payload.performer_id,
        source="session_manager",
        session_id=new_session_id,
        start_time=now,
        is_training_data=is_training,
        session_notes=payload.session_notes,
        training_intent_label=payload.training_intent_label,
    )

    from apps.schema_recorder.config import LOG_ROOT
    from utils.paths import session_log_path

    log_path = session_log_path(
        log_root=LOG_ROOT,
        user_id=out.user_id,
        session_id=new_session_id,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    append_event(user_id=out.user_id, session_id=str(out.session_id), message=out)

    return out


def end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput:
    if not payload.session_id:
        raise SessionError("session_id is required")

    session_id = payload.session_id
    session = _sessions.get(session_id)
    if not session or session["user_id"] != payload.user_id:
        raise SessionNotFound("Session not found or user mismatch")

    if session.get("status") == "closed":
        raise SessionError("Session already closed")

    session["end_time"] = payload.end_time
    session["status"] = "closed"

    out = SessionManagerEndOutput(
        schema_version=payload.schema_version,
        record_id=payload.record_id,
        user_id=payload.user_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        source="session_manager",
        performer_id=payload.performer_id,
        end_time=payload.end_time,
    )
    append_event(user_id=out.user_id, session_id=str(out.session_id), message=out)

    return out
