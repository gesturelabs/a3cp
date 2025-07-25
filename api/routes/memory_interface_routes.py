# api/routes/memory_interface_routes.py
from fastapi import APIRouter, HTTPException

from schemas.memory_interface.memory_interface import (
    MemoryAuditEntry,
    MemoryQueryResult,
)

router = APIRouter()


@router.post("/", response_model=MemoryQueryResult)
def query_memory_hints(entry: MemoryAuditEntry) -> MemoryQueryResult:
    """
    Stubbed memory interface endpoint.
    Accepts an audit entry and returns memory-derived intent hints.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
