# api/routes/sound_infer.py

from fastapi import APIRouter
from datetime import datetime
from api.schemas.sound_infer import A3CPMessage, IntentCandidate

router = APIRouter()

@router.post("/infer/", response_model=A3CPMessage)
async def infer_sound():
    # Return dummy A3CPMessage (placeholder for actual sound model inference)
    return A3CPMessage(
        classifier_output=[
            IntentCandidate(label="need-help", confidence=0.91),
            IntentCandidate(label="pain", confidence=0.06),
            IntentCandidate(label="hungry", confidence=0.03)
        ],
        record_id="rec-audio-dummy",
        user_id="user-test",
        session_id="sess-test",
        timestamp=datetime.now(),
        modality="sound",
        source="simulator",
        vector="vector-audio-ref"
    )
