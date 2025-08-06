# api/routes/session_manager_end_routes.py

# api/routes/session_manager_end_routes.py


from fastapi import APIRouter, HTTPException

from schemas.session_manager_end.session_manager_end import SessionEndEvent

router = APIRouter()

# Temporary in-memory session store shared or separate as needed
_sessions = {}


@router.post("/end", response_model=SessionEndEvent)
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
