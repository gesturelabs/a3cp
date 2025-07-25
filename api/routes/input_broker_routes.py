# api/routes/input_broker_routes.py
from fastapi import APIRouter, HTTPException

from schemas.input_broker.input_broker import AlignedInputBundle

router = APIRouter()


@router.post("/", response_model=AlignedInputBundle)
def receive_aligned_bundle(bundle: AlignedInputBundle) -> AlignedInputBundle:
    """
    Stubbed input broker endpoint.
    Accepts an aligned multimodal bundle from upstream classifiers.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
