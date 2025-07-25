# api/routes/feedback_log_routes.py
from fastapi import APIRouter, HTTPException

from schemas.feedback_log.feedback_log import FeedbackLogEntry

router = APIRouter()


@router.post("/", response_model=FeedbackLogEntry)
def log_feedback(entry: FeedbackLogEntry) -> FeedbackLogEntry:
    """
    Stubbed feedback logging endpoint.
    Accepts a caregiver clarification log entry.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
