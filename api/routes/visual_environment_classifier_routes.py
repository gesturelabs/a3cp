# api/routes/visual_environment_classifier_routes.py
from fastapi import APIRouter, HTTPException

from schemas.visual_environment_classifier.visual_environment_classifier import (
    VisualEnvironmentPrediction,
)

router = APIRouter()


@router.post("/", response_model=VisualEnvironmentPrediction)
def classify_visual_environment(
    payload: VisualEnvironmentPrediction,
) -> VisualEnvironmentPrediction:
    """
    Stub endpoint for environment classification from video frame.
    Typically called by camera or scene recognition module.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
