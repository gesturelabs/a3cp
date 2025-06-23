# tests/schemas/test_inference_trace.py

from datetime import datetime
from uuid import uuid4

from schemas.inference_trace import InferenceTrace


def test_valid_inference_trace():
    trace = InferenceTrace(
        record_id=uuid4(),
        session_id="a3cp_sess_2025-06-23_user01",
        timestamp=datetime.utcnow(),
        module_name="gesture_classifier",
        model_version="v3.2.1",
        predicted_intent="eat",
        intent_confidence=0.93,
        candidate_intents={"eat": 0.93, "drink": 0.04, "rest": 0.03},
        memory_hint_used=True,
        fallback_triggered=False,
        memory_fallback_suggestions=["rest", "drink"],
        decision_reasoning="high confidence + top memory boost",
        downstream_decision="eat",
    )

    assert trace.predicted_intent == "eat"
    assert trace.intent_confidence > 0.9
