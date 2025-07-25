# api/routes/output_expander_routes.py
from fastapi import APIRouter, HTTPException

from schemas.output_expander.output_expander import (OutputExpansionInput,
                                                     OutputExpansionResult)

router = APIRouter()


@router.post("/", response_model=OutputExpansionResult)
def expand_output_phrase(
    input_data: OutputExpansionInput,
) -> OutputExpansionResult:
    """
    Stubbed output expander endpoint.
    Converts final decision intent into a personalized phrase using context and user profile.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
