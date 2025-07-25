# api/routes/output_planner_routes.py
from fastapi import APIRouter, HTTPException

from schemas.output_planner.output_planner import (OutputPlannerDecision,
                                                   OutputPlannerInput)

router = APIRouter()


@router.post("/", response_model=OutputPlannerDecision)
def plan_output_delivery(input_data: OutputPlannerInput) -> OutputPlannerDecision:
    """
    Stubbed output planner endpoint.
    Selects output modality and prepares the AAC phrase for rendering.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
