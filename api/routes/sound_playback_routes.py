# api/routes/sound_playback_routes.py
from fastapi import APIRouter, HTTPException

from schemas.sound_playback.sound_playback import AudioPlaybackRequest

router = APIRouter()


@router.post("/", response_model=AudioPlaybackRequest)
def playback_audio(request: AudioPlaybackRequest) -> AudioPlaybackRequest:
    """
    Stub endpoint for logging or triggering audio playback.
    Accepts metadata about the file to be played.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
