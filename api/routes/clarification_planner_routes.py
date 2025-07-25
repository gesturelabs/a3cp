# api/routes/clarification_planner_routes.py
from fastapi import APIRouter, HTTPException

from schemas.clarification_planner.clarification_planner import (
    ClarificationPlannerInput,
    ClarificationPlannerOutput,
)

router = APIRouter()


@router.post("/", response_model=ClarificationPlannerOutput)
def run_clarification_planner(
    input_data: ClarificationPlannerInput,
) -> ClarificationPlannerOutput:
    """
    Stubbed clarification planner endpoint.
    Returns mock clarification metadata.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
