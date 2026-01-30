# apps/session_manager/routes/router.py

from fastapi import APIRouter, HTTPException

from apps.session_manager import service
from schemas import (
    SessionManagerEndInput,
    SessionManagerEndOutput,
    SessionManagerStartInput,
    SessionManagerStartOutput,
)

router = APIRouter(prefix="/session_manager", tags=["session_manager"])


@router.post("/sessions.start", response_model=SessionManagerStartOutput)
def start_session(payload: SessionManagerStartInput) -> SessionManagerStartOutput:
    try:
        return service.start_session(payload)
    except service.SessionAlreadyActive as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except service.SessionError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/sessions.end", response_model=SessionManagerEndOutput)
def end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput:
    try:
        return service.end_session(payload)
    except service.SessionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except service.SessionUserMismatch as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except service.SessionAlreadyClosed as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except service.SessionError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
