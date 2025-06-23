import uuid
from datetime import datetime

from schemas.clarification_event import ClarificationEvent


def test_valid_clarification_event():
    event = ClarificationEvent(
        schema_version="1.0.0",
        record_id=uuid.uuid4(),
        user_id="elias01",
        session_id="a3cp_sess_2025-06-23_elias01",
        timestamp=datetime.now(),
        trigger_reason="low_confidence",
        clarification_type="multiple_choice",
        options_presented=["eat", "drink", "rest"],
        user_response="drink",
        resolved_intent="drink",
        clarification_successful=True,
        notes="Clarification required due to <0.6 confidence",
    )

    assert event.schema_version == "1.0.0"
    assert event.user_response == "drink"
