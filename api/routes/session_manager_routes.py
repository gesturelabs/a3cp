# api/routes/session_manager_routes.py

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from schemas.session_manager_end.session_manager_end import SessionEndEvent
from schemas.session_manager_start.session_manager_start import (
    SessionStartRequest,
    SessionStartResponse,
)

router = APIRouter(prefix="/session_manager", tags=["session_manager"])

# Temporary in-memory store for sessions
_sessions = {}


@router.post("/sessions.start", response_model=SessionStartResponse)
def start_session(event: SessionStartRequest) -> SessionStartResponse:
    """
    Stub for beginning a user session.
    Accepts a start request and returns session metadata with assigned session_id and timestamp.
    """
    new_session_id = f"sess_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)

    is_training = (
        event.is_training_data if event.is_training_data is not None else False
    )

    _sessions[new_session_id] = {
        "user_id": event.user_id,
        "start_time": now,
        "is_training_data": is_training,
        "session_notes": event.session_notes,
        "performer_id": event.performer_id,
        "training_intent_label": event.training_intent_label,
        "status": "active",
    }

    return SessionStartResponse(
        session_id=new_session_id,
        start_time=now,
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id=event.user_id,
        timestamp=now,
        source="session_manager",
        modality=None,
        performer_id=event.performer_id,
        is_training_data=is_training,
        session_notes=event.session_notes,
        training_intent_label=event.training_intent_label,
    )


@router.post("/sessions.end", response_model=SessionEndEvent)
def end_session(event: SessionEndEvent) -> SessionEndEvent:
    """
    Stub for ending a user session.
    Accepts an end event and returns the echoed structure.
    """
    session = _sessions.get(event.session_id)
    if not session or session["user_id"] != event.user_id:
        raise HTTPException(
            status_code=404, detail="Session not found or user mismatch"
        )

    if session.get("status") == "closed":
        raise HTTPException(status_code=400, detail="Session already closed")

    # Mark session closed
    session["end_time"] = event.end_time
    session["status"] = "closed"

    # Return the event as confirmation
    return event
