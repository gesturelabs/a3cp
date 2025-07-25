# api/routes/landmark_visualizer_routes.py
from fastapi import APIRouter, HTTPException

from schemas.landmark_visualizer.landmark_visualizer import (
    LandmarkVisualizerInput, LandmarkVisualizerOutput)

router = APIRouter()


@router.post("/", response_model=LandmarkVisualizerOutput)
def render_landmark_visualization(
    request: LandmarkVisualizerInput,
) -> LandmarkVisualizerOutput:
    """
    Stubbed landmark visualizer endpoint.
    Accepts recorded landmark data and returns rendering metadata.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
