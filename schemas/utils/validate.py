# schemas/utils/validate.py

from pydantic import ValidationError

from schemas.a3cp_core.a3cp_message import A3CPMessage


def validate_a3cp_message(data: dict) -> A3CPMessage:
    """
    Validates that the payload conforms to core A3CPMessage schema.
    Allows extra fields for partial pipeline state.
    """
    try:
        return A3CPMessage(**data)
    except ValidationError as e:
        print("A3CPMessage validation error:", e)
        raise
