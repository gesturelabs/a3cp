# Module: streamer

## Purpose
The `streamer` module is responsible for real-time capture and processing of video-based user actions. It extracts structured representations (e.g., body landmarks) from the camera feed and packages them into schema-compliant records. These records can be used for both model training and live inference, depending on the system state.

## Why It Matters
This module is the primary entry point for collecting gestural data from users. Without it, the A3CP system cannot observe or interpret user intent through nonverbal input. It ensures that high-quality, structured input is continuously available for both learning and communication.

## Responsibilities
- Capturing real-time video input from a connected camera device.
- Extracting 2D/3D landmarks or other body pose features.
- Packaging each segment into a valid `RawActionRecord` conforming to `schema.json`.
- Streaming records to either:
  - The training dataset (if labeled by the caregiver).
  - The gesture classifier module (if in inference mode).
- Tagging records with session metadata for auditability and traceability.
- Optionally tagging training examples with `intent_label`.

## Not Responsible For
- Audio capture or transcription (handled by `audio_streamer`).
- Inference/classification logic (handled by `gesture_classifier`).
- CARE Engine decision-making or AAC output generation.
- Persisting raw video files (landmark vectors are saved instead).

## Inputs
- Live video feed (camera device).
- Session metadata (user ID, session ID, timestamp).
- Optional caregiver input for `intent_label`.

## Outputs
- Schema-compliant JSON or Parquet records containing:
  - Landmarks or pose vectors.
  - Source/modality/session metadata.
  - Optional training label (`intent_label`) if provided.
- Logs to the session history and provenance systems.

## CARE Integration
- **Feeds**: Sends structured records to the `gesture_classifier` module in live mode.
- **Logs for**: CARE clarification decisions by providing labeled training examples.
- **Triggered by**: Session start or partner-initiated data recording.
- **Supports**: Memory learning by contributing labeled gestures to the user’s training dataset.

## Functional Requirements
- F1. Must extract feature vectors (e.g., pose landmarks) in real time from video input.
- F2. Must produce valid schema-compliant records for each event or segment.
- F3. Must support both training and inference modes, dynamically switchable.
- F4. Must preserve session-level metadata and traceability across records.

## Non-Functional Requirements
- NF1. Must operate under low-latency constraints to support real-time classification.
- NF2. Must allow modular extension (e.g., additional input sources like depth camera).
- NF3. Must avoid saving raw video for privacy and storage efficiency.
- NF4. Must validate output schema prior to downstream transmission or saving.

## Developer(s)
Ilona

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
