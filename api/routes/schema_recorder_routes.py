# api/routes/schema_recorder_routes.py
from fastapi import APIRouter, HTTPException

from schemas.schema_recorder.schema_recorder import RecorderConfig

router = APIRouter()


@router.post("/", response_model=RecorderConfig)
def configure_schema_recorder(config: RecorderConfig) -> RecorderConfig:
    """
    Stub for schema recorder configuration.
    Accepts a logging configuration and returns confirmation.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
