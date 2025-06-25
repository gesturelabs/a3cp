# Module: speech_transcriber

## Purpose
Captures and transcribes caregiver or partner speech in real time using streaming automatic speech recognition (ASR). Provides continuously updated transcripts to downstream modules, enabling contextual understanding, topic detection, and clarification planning.

## Why It Matters
Real-time partner speech provides crucial context for interpreting ambiguous gestures or vocalizations. Transcriptions inform the CARE Engine about questions, topics, and conversational cues, enhancing intent inference and guiding when clarifications are needed.

## Responsibilities
- Capture live audio from the microphone during interaction sessions
- Run low-latency streaming ASR using engines such as Whisper.cpp or Vosk
- Emit:
  - Partial transcripts (live updates)
  - Finalized transcript segments with timestamps
  - Optional ASR confidence scores
- Attach session metadata (user pseudonym, session_id, timestamp)
- Stream updates to downstream modules (e.g., `speech_context_inferer`)
- Optionally log transcripts in `.jsonl` format for audit and training

## Not Responsible For
- Interpreting or tagging the transcript
- Performing intent inference or classification
- Handling playback or annotation of recorded speech
- Running model training or managing ASR model registry

## Inputs
- Live audio stream from caregiver/partner microphone
- Session metadata:
  - `session_id`, `timestamp`, `user_id` or `pseudonym`
- ASR backend configuration (e.g., language, model path)

## Outputs
- Partial transcript updates (as they stream in)
- Finalized transcript segments with:
  - Timestamps
  - Confidence scores (if supported)
- Streaming JSON messages to downstream consumers
- Optional `.jsonl` transcript log file (e.g., `transcripts/session_<id>.jsonl`)

## CARE Integration
Feeds transcripts into `speech_context_inferer`, which analyzes them for topic cues, questions, and prompt relevance. This context influences CARE Engine behavior and can trigger clarification if needed.

## Functional Requirements
- F1. Continuously capture microphone input during user interaction sessions
- F2. Transcribe speech using low-latency ASR engine (e.g., Whisper.cpp, Vosk)
- F3. Emit both partial and finalized transcript segments with timestamps
- F4. Include confidence scores if supported by ASR backend
- F5. Forward transcript segments to contextual analysis modules

## Non-Functional Requirements
- NF1. Must maintain latency under 300ms for short utterances
- NF2. Must support multilingual transcription where configured
- NF3. Must run on-device or local network for data privacy
- NF4. Must recover from silence, noise, or dropped audio frames
- NF5. Must optionally log transcripts to `.jsonl` for audit, debugging, or retraining

## Developer(s)
Unassigned

## Priority
High

## Example Files
- `examples/partial_transcript.json`
- `examples/final_transcript_with_confidence.json`
