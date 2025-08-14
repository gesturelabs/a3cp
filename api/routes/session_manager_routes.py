# api/routes/session_manager_routes.py

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from schemas import (
    SessionManagerEndInput,
    SessionManagerEndOutput,
    SessionManagerStartInput,
    SessionManagerStartOutput,
)

router = APIRouter(prefix="/session_manager", tags=["session_manager"])

# Temporary in-memory store for sessions
_sessions: dict[str, dict] = {}


@router.post("/sessions.start", response_model=SessionManagerStartOutput)
def start_session(payload: SessionManagerStartInput) -> SessionManagerStartOutput:
    """
    Begin a user session. Returns assigned session_id and session metadata.
    """
    new_session_id = f"sess_{uuid.uuid4().hex[:8]}"
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

    # Build output (session_id enforced non-empty by model validator)
    return SessionManagerStartOutput(
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


@router.post("/sessions.end", response_model=SessionManagerEndOutput)
def end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput:
    if not payload.session_id:  # static and runtime safety
        raise HTTPException(status_code=400, detail="session_id is required")

    session_id = payload.session_id  # now typed as str after the guard
    session = _sessions.get(session_id)
    if not session or session["user_id"] != payload.user_id:
        raise HTTPException(
            status_code=404, detail="Session not found or user mismatch"
        )

    if session.get("status") == "closed":
        raise HTTPException(status_code=400, detail="Session already closed")

    session["end_time"] = payload.end_time
    session["status"] = "closed"

    return SessionManagerEndOutput(
        schema_version=payload.schema_version,
        record_id=payload.record_id,
        user_id=payload.user_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        source="session_manager",
        performer_id=payload.performer_id,
        end_time=payload.end_time,
    )
