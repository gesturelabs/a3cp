# api/routes/speech_context_classifier_routes.py
from fastapi import APIRouter, HTTPException

from schemas.speech_context_classifier.speech_context_classifier import (
    SpeechContextClassifierInput,
    SpeechContextClassifierOutput,
)

router = APIRouter()


@router.post("/", response_model=SpeechContextClassifierOutput)
def classify_speech_context(
    payload: SpeechContextClassifierInput,
) -> SpeechContextClassifierOutput:
    """
    Stub endpoint for contextual speech classification.
    Accepts transcribed partner speech and user vocabulary to infer likely intent(s).
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
