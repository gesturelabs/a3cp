# api/routes/speech_transcriber_routes.py
from fastapi import APIRouter, HTTPException

from schemas.speech_transcriber.speech_transcriber import \
    SpeechTranscriptSegment

router = APIRouter()


@router.post("/", response_model=SpeechTranscriptSegment)
def receive_transcript_segment(
    payload: SpeechTranscriptSegment,
) -> SpeechTranscriptSegment:
    """
    Stub endpoint for receiving a transcribed speech segment.
    Typically used for ASR (Automatic Speech Recognition) output.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
