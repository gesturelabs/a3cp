# api/routes/sound_classifier_routes.py
from fastapi import APIRouter, HTTPException

from schemas.sound_classifier.sound_classifier import (SoundClassifierInput,
                                                       SoundClassifierOutput)

router = APIRouter()


@router.post("/", response_model=SoundClassifierOutput)
def classify_sound(input_data: SoundClassifierInput) -> SoundClassifierOutput:
    """
    Stub endpoint for sound intent classification.
    Accepts audio payload and returns ranked intent predictions.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
