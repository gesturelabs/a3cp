# api/routes/landmark_extractor_routes.py
from fastapi import APIRouter, HTTPException

from schemas.landmark_extractor.landmark_extractor import LandmarkExtractorOutput

router = APIRouter()


@router.post("/", response_model=LandmarkExtractorOutput)
def extract_landmarks(output: LandmarkExtractorOutput) -> LandmarkExtractorOutput:
    """
    Stubbed landmark extractor endpoint.
    Accepts and returns landmark feature vectors from RGB frame analysis.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
