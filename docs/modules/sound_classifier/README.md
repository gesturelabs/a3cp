# Module: sound_classifier

## Purpose
The `sound_classifier` module converts short audio recordings into ranked intent predictions using a pre-trained, user-specific classification model. It extracts acoustic features (e.g., MFCCs), runs inference, and returns structured predictions to the CARE Engine for downstream decision-making.

| Field                  | Value                                        |
|------------------------|----------------------------------------------|
| **Module Name**        | `sound_classifier`                           |
| **Module Type**        | `classifier`                                 |
| **Inputs From**        | `audio_feed_worker`, `model_registry`        |
| **Outputs To**         | `input_broker`                               |
| **Produces A3CPMessage?** | ✅ Yes (classifier_output only)           |



## Why It Matters
For users with limited or non-traditional speech, vocalizations may carry intentional signals that are not captured through gesture alone. This module enables interpretation of such signals, broadening communication support and improving system responsiveness by incorporating audio-based intent inference alongside contextual and visual cues.

## Responsibilities
- Normalize and validate audio input (mono, 16-bit PCM)
- Extract audio features (e.g., MFCCs, spectrograms) suitable for the user’s model
- Load the correct user-specific model and label encoder from the model registry
- Run inference and generate ranked intent candidates with confidence scores
- Return results in schema-compliant `classifier_output` format
- Log each inference event to `inference_trace.jsonl` with metadata

## Not Responsible For
- Saving audio files to disk
- Playing audio or enabling annotation interfaces
- Training or fine-tuning models
- Persisting structured outputs outside of inference trace logs

## Inputs
- Live or buffered audio waveform
- Sampling rate (e.g., 16kHz or 44.1kHz)
- Session metadata:
  - `user_id`, `session_id`, `timestamp`, `modality`, `source`
- User-specific audio model and associated class label mapping

## Outputs
- `classifier_output` object containing:
  - Ranked list of predicted intents with confidence scores
  - Optional model metadata (version, timestamp)
- Logged record in `inference_trace.jsonl` with:
  - `timestamp`, `user_id`, `session_id`, `modality`, `source`, `model_version`, and raw prediction


{
  "schema_version": "1.0.0",
  "record_id": "uuid4-here",
  "user_id": "elias01",
  "session_id": "sess_2025-07-01_elias01",
  "timestamp": "2025-07-01T13:21:11.654Z",
  "modality": "audio",
  "source": "communicator",
  "classifier_output": {
    "intent": "play",
    "confidence": 0.87
  },
  "model_version": "sound_model_v2.3"
}


## CARE Integration

- **Upstream**: Receives buffered or streamed audio from `audio_feed_worker`
- **Downstream**: Sends classifier predictions to `input_broker` for multimodal fusion
- **Role in Pipeline**: Provides audio-based intent predictions via the `classifier_output` field in the `A3CPMessage`
- **API Note**: May be invoked via `/api/sound/infer/`, but is typically called internally by the CARE system
- **Integration Point**: Participates in early-stage inference, supporting parallel inputs from gesture and contextual classifiers


## Functional Requirements
- F1. Accept and normalize live or buffered audio input (mono, 16-bit PCM)
- F2. Extract standardized audio features (e.g., MFCCs) compatible with the user’s model
- F3. Lookup and load user-specific classification model and class labels from registry
- F4. Run inference and return top-N ranked intent candidates with confidence scores
- F5. Log each inference result to `inference_trace.jsonl` with required metadata
- F6. Return results using the `classifier_output` structure in the A3CP schema

## Non-Functional Requirements
- NF1. Inference latency must be <300ms for audio clips under 3 seconds
- NF2. Support input at multiple sample rates (e.g., 16kHz, 44.1kHz); resample if needed
- NF3. Gracefully handle invalid, corrupt, or silent audio input
- NF4. Operate in a stateless, concurrent-safe manner (supporting multiple users)
- NF5. All predictions must pass schema validation and include class labels from model registry
- NF6. Cache or preload models to avoid cold-start latency
- NF7. Ensure audio is normalized (mono, 16-bit PCM) before feature extraction

## Developer(s)
Unassigned

## Priority
High

-------------------------------------------------------------------------------
✅ SCHEMA COMPLIANCE SUMMARY
-------------------------------------------------------------------------------

This module emits partial `A3CPMessage` records with the `classifier_output` field populated:

Required fields:
- `schema_version`, `record_id`, `timestamp`, `user_id`, `session_id`
- `modality = "audio"`, `source = "communicator"`
- `classifier_output = { "intent": <str>, "confidence": <float> }`
Optional:
- `model_version`, `inference_latency`, or other classifier metadata

These messages must be valid under `SCHEMA_REFERENCE.md` and are passed to `input_broker`.

## Example Files
- [sample_input_audio.wav](./sample_input_audio.wav)
- [sample_classifier_output.json](./sample_classifier_output.json)
- [inference_trace.jsonl](./inference_trace.jsonl)
