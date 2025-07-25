# api/routes/session_manager_routes.py
from fastapi import APIRouter, HTTPException

from schemas.session_manager.session_manager import SessionEndEvent, SessionStartEvent

router = APIRouter()


@router.post("/start", response_model=SessionStartEvent)
def start_session(event: SessionStartEvent) -> SessionStartEvent:
    """
    Stub for beginning a user session.
    Accepts a start event and returns the echoed structure.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/end", response_model=SessionEndEvent)
def end_session(event: SessionEndEvent) -> SessionEndEvent:
    """
    Stub for ending a user session.
    Accepts an end event and returns the echoed structure.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
