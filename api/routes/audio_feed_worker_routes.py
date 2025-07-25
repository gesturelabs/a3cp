# api/routes/audio_feed_worker_routes.py

from fastapi import APIRouter

from schemas.audio_feed_worker.audio_feed_worker import (
    AudioChunkMetadata,
    AudioFeedWorkerConfig,
)

router = APIRouter()


@router.post("/", response_model=AudioChunkMetadata)
def simulate_audio_capture(config: AudioFeedWorkerConfig) -> AudioChunkMetadata:
    """
    Simulate an audio capture from a given device config.
    Returns metadata with fake encoded waveform.
    """
    return AudioChunkMetadata(**AudioChunkMetadata.example_output())
