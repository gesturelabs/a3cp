# api/routes/retraining_scheduler_routes.py
from fastapi import APIRouter, HTTPException

from schemas.retraining_scheduler.retraining_scheduler import (
    RetrainingDecisionLog,
    RetrainingRequest,
)

router = APIRouter()


@router.post("/", response_model=RetrainingDecisionLog)
def trigger_retraining(input_data: RetrainingRequest) -> RetrainingDecisionLog:
    """
    Stub for retraining scheduler.
    Evaluates whether retraining should be triggered based on input metadata and policy.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
