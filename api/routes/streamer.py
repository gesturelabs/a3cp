# api/routes/streamer.py

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from api.schemas.streamer import RawInput

router = APIRouter()


@router.post("/", summary="Simulate raw input capture")
async def simulate_raw_input(data: RawInput):
    if not data.consent_given:
        raise HTTPException(
            status_code=403, detail="Consent is required for input capture."
        )

    record_id = f"rec-{uuid4()}"
    ts = datetime.now().isoformat()

    return {
        "status": "accepted",
        "record_id": record_id,
        "timestamp": ts,
        "modality": data.modality,
        "input_size": len(data.raw_input_audio or data.raw_input_video or []),
    }
