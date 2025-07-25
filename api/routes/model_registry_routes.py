# api/routes/model_registry_routes.py
from fastapi import APIRouter, HTTPException

from schemas.model_registry.model_registry import ModelRegistryEntry

router = APIRouter()


@router.post("/", response_model=ModelRegistryEntry)
def register_model(entry: ModelRegistryEntry) -> ModelRegistryEntry:
    """
    Stubbed model registry endpoint.
    Accepts a new model metadata record for logging and lookup.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
