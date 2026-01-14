# Module: input_broker

## Purpose
Aligns timestamped, classifier-generated A3CPMessages from multiple input modalities (e.g., gesture, audio, speech) into synchronized bundles for downstream processing.

| Field                  | Value                                                              |
|------------------------|--------------------------------------------------------------------|
| **Module Name**        | `input_broker`                                                     |
| **Module Type**        | `coordinator`                                                      |
| **Inputs From**        | `gesture_classifier`, `sound_classifier`, `speech_context_classifier`, `visual_environment_classifier` |
| **Outputs To**         | `confidence_evaluator`, `schema_recorder`                          |
| **Produces A3CPMessage?** | ❌ No (passes through and rebundles existing messages)

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

{
  "stream_segment_id": "u01_seg_0005",
  "timestamp": "2025-07-01T13:33:21.004Z",
  "session_id": "sess_2025-07-01_u01",
  "messages": [
    { ...A3CPMessage from gesture_classifier... },
    { ...A3CPMessage from sound_classifier... },
    { ...A3CPMessage from speech_context_classifier... }
  ]
}

## CARE Integration
- **Upstream**: Receives fully validated `A3CPMessage` records from perceptual modules (gesture, audio, speech, visual)
- **Downstream**: Emits temporally aligned input bundles to `confidence_evaluator` and `schema_recorder`
- **Role in CARE Loop**: Provides the first fusion point for synchronizing parallel classifier outputs before scoring or clarification

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

-------------------------------------------------------------------------------
✅ SCHEMA COMPLIANCE SUMMARY
-------------------------------------------------------------------------------

This module does **not** produce new `A3CPMessage` records. It receives and buffers validated messages from upstream classifiers and passes them through in aligned multimodal bundles.

Responsibilities:
- Validate and group existing schema-compliant messages by `timestamp` and `session_id`
- Does not mutate or emit new fields
- May annotate messages with shared `stream_segment_id` or pass-through metadata for downstream bundling

Schema-wrapped output is ensured by upstream modules.


## Example Files
- [sample_input.json](_/sample_input.json)
- [sample_output.json](_/sample_output.json)
- [schema.json](_/schema.json)
