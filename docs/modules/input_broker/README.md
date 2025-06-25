# Module: input_broker

## Purpose
Aligns timestamped, classifier-generated A3CPMessages from multiple input modalities (e.g., gesture, audio, speech) into synchronized bundles for downstream processing.

## Why It Matters
Synchronized, multimodal input is essential for reliable interpretation of user intent. By aligning temporally related messages, this module ensures that the CARE Engine can reason over coherent input without confusion from modality latency or skew.

## Responsibilities
- Buffer incoming A3CPMessages by modality and timestamp
- Align messages within a configurable rolling inference window
- Emit aligned input bundles to downstream modules (e.g., ConfidenceEvaluator)
- Gracefully handle asynchronous or delayed inputs

## Not Responsible For
- Preprocessing of input signals (e.g., audio or gesture vector extraction)
- Scoring, fusion, or final output decisions
- Clarification planning or model inference

## Inputs
- A3CPMessages from input sources such as:
  - Gesture Processor
  - Sound Processor
  - SpeechTranscriber
- Each message includes:
  - `timestamp`
  - `modality`
  - `classifier_output`
  - `user_id`, `session_id`

## Outputs
- Temporally aligned input bundles:
  - Grouped A3CPMessages from multiple modalities
  - Shared `stream_segment_id`, `timestamp`, `session_id`
- Forwarded to:
  - ConfidenceEvaluator

## CARE Integration
Acts as the first fusion step in the CARE Engine pipeline. Receives and synchronizes inputs from all perceptual modules before passing aligned bundles to ConfidenceEvaluator for weighted scoring.

## Functional Requirements
- F1. Must accept timestamped A3CPMessages from all input modalities
- F2. Must align messages within a configurable rolling time window
- F3. Must discard or defer stale or temporally misaligned messages

## Non-Functional Requirements
- NF1. Must operate within <50ms latency under normal load
- NF2. Must not drop valid messages unnecessarily
- NF3. Must ensure temporal coherence across modalities
- NF4. Must handle asynchronous input arrival without blocking

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
