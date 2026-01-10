# apps/session_manager/service.py


import uuid
from datetime import datetime, timezone

from apps.session_manager import repository
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
    """
    Begin a user session. Returns assigned session_id and session metadata.
    """
    new_session_id = f"sess_{uuid.uuid4().hex[:16]}"
    while new_session_id in _sessions:
        new_session_id = f"sess_{uuid.uuid4().hex[:16]}"

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
    repository.append_session_event(
        user_id=out.user_id,
        session_id=str(out.session_id),
        message=out,
    )

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
    repository.append_session_event(
        user_id=out.user_id,
        session_id=str(out.session_id),
        message=out,
    )

    return out
