# api/routes/session_manager_routes.py


from fastapi import APIRouter, HTTPException

from schemas.session_manager.session_manager import (
    SessionEndEvent,
    SessionStartRequest,
    SessionStartResponse,
)

router = APIRouter()


@router.post("/start", response_model=SessionStartResponse)
def start_session(event: SessionStartRequest) -> SessionStartResponse:
    """
    Stub for beginning a user session.
    Accepts a start request and returns session metadata with assigned session_id and timestamp.
    """
    # Replace with real logic in implementation
    raise HTTPException(status_code=501, detail="Not implemented yet")

    # Example (if implemented):
    # new_session_id = f"sess_{uuid.uuid4().hex[:8]}"
    # now = datetime.utcnow()
    # return SessionStartResponse(
    #     session_id=new_session_id,
    #     start_time=now,
    #     **event.dict()
    # )


@router.post("/end", response_model=SessionEndEvent)
def end_session(event: SessionEndEvent) -> SessionEndEvent:
    """
    Stub for ending a user session.
    Accepts an end event and returns the echoed structure.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
