# api/routes/gesture_infer.py

from fastapi import APIRouter
from datetime import datetime
from api.schemas.gesture_infer import A3CPMessage, IntentCandidate

router = APIRouter()

@router.post("/gesture/infer/", response_model=A3CPMessage)
async def infer_gesture():
    # Return dummy A3CPMessage (placeholder for model inference output)
    return A3CPMessage(
        classifier_output=[
            IntentCandidate(label="want-drink", confidence=0.92),
            IntentCandidate(label="need-help", confidence=0.07)
        ],
        record_id="rec-dummy-001",
        user_id="user-test",
        session_id="sess-test",
        timestamp=datetime.now(),
        modality="gesture",
        source="simulator",
        vector="vector-dummy-ref"
    )
