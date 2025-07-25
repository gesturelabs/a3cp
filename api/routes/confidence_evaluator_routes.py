# api/routes/confidence_evaluator_routes.py
from fastapi import APIRouter, HTTPException

from schemas.confidence_evaluator.confidence_evaluator import (
    ConfidenceEvaluatorInput,
    ConfidenceEvaluatorOutput,
)

router = APIRouter()


@router.post("/", response_model=ConfidenceEvaluatorOutput)
def run_confidence_evaluator(
    input_data: ConfidenceEvaluatorInput,
) -> ConfidenceEvaluatorOutput:
    """
    Stubbed confidence evaluator endpoint.
    Returns mock scored output with audit metadata.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
