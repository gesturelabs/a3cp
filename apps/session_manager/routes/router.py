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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/sessions.end", response_model=SessionManagerEndOutput)
def end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput:
    try:
        return service.end_session(payload)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower() or "mismatch" in msg.lower():
            raise HTTPException(status_code=404, detail=msg) from e
        raise HTTPException(status_code=400, detail=msg) from e
