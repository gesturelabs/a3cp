# api/routes/model_trainer_routes.py
from fastapi import APIRouter, HTTPException

from schemas.model_trainer.model_trainer import TrainingLogEntry, TrainingRequest

router = APIRouter()


@router.post("/", response_model=TrainingLogEntry)
def train_model(request: TrainingRequest) -> TrainingLogEntry:
    """
    Stubbed model trainer endpoint.
    Accepts a training request and returns training log metadata.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
