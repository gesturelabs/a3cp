# api/routes/gesture_classifier_routes.py
from fastapi import APIRouter, HTTPException

from schemas.gesture_classifier.gesture_classifier import (
    GestureClassifierInput,
    GestureClassifierOutput,
)

router = APIRouter()


@router.post("/", response_model=GestureClassifierOutput)
def run_gesture_classifier(
    input_data: GestureClassifierInput,
) -> GestureClassifierOutput:
    """
    Stubbed gesture classifier endpoint.
    Accepts landmark features and returns predicted intent scores.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
