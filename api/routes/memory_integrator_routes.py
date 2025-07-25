# api/routes/memory_integrator_routes.py
from fastapi import APIRouter, HTTPException

from schemas.memory_integrator.memory_integrator import (
    MemoryIntegratorInput, MemoryIntegratorOutput)

router = APIRouter()


@router.post("/", response_model=MemoryIntegratorOutput)
def adjust_with_memory(input_data: MemoryIntegratorInput) -> MemoryIntegratorOutput:
    """
    Stubbed memory integrator endpoint.
    Applies memory-derived adjustments to intent classifier outputs.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
