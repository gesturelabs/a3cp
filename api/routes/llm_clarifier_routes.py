# api/routes/llm_clarifier_routes.py
from fastapi import APIRouter, HTTPException

from schemas.llm_clarifier.llm_clarifier import (LLMClarifierInput,
                                                 LLMClarifierOutput)

router = APIRouter()


@router.post("/", response_model=LLMClarifierOutput)
def generate_clarification_prompt(input_data: LLMClarifierInput) -> LLMClarifierOutput:
    """
    Stubbed LLM clarifier endpoint.
    Generates a clarification prompt using intent candidates and context flags.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
