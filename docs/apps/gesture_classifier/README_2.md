# Module: gesture_classifier_2

## Purpose

Classifies bounded gesture landmark captures into structured intent confidence distributions.
The module performs per-user gesture inference over internally segmented windows, aggregates window-level scores into a single capture-level distribution, and preserves full inference traces for research, retraining, and auditability.

| Field                      | Value                                      |
|----------------------------|--------------------------------------------|
| **Module Name**            | `gesture_classifier`                       |
| **Module Type**            | `classifier`                               |
| **Inputs From**            | `landmark_extractor`, `model_registry`     |
| **Outputs To**             | `input_broker`                             |
| **Produces A3CPMessage?**  | ✅ Yes (`classifier_output` only)          |


---

## Why It Matters

Gesture classification is the foundation of nonverbal intent inference in A3CP.
By producing reproducible, per-user intent confidence distributions from bounded captures, the module enables CARE reasoning while maintaining strict auditability and deterministic replay.

The MVP design prioritizes:

- Determinism
- Schema stability
- Per-user model isolation
- Conservative reject behavior
- Full reproducibility from stored feature artifacts


---

## Responsibilities

- Accept bounded landmark feature artifacts (`raw_features_ref`) and required metadata (`user_id`, `session_id`, `timestamp`)
- Load and cache user-specific model artifacts from `model_registry`
- Perform internal windowing over bounded feature tensors (`length_frames=16`, `stride_frames=5`)
- Score each window using a per-user temporal encoder + prototype classifier
- Apply per-window reject criteria
- Aggregate window-level scores into a single capture-level intent confidence distribution
- Emit exactly one A3CPMessage per bounded capture
- Validate emitted records against the A3CPMessage schema
- Log full per-window inference traces to `inference_trace.jsonl`


---

## Not Responsible For

- Consent collection, video capture, or landmark extraction
- Cross-capture temporal reasoning
- Event latching or cooldown logic
- Multimodal fusion
- UI rendering or clarification logic
- Session lifecycle management
- Long-term feature storage orchestration


---

## Inputs

- `raw_features_ref`: Reference to bounded landmark feature artifact produced by `landmark_extractor` (dense `(T, D)` tensor + metadata)
- `user_id`, `session_id`, `timestamp`
- Model artifacts from `model_registry`:
  - Temporal encoder weights (ONNX)
  - `label_map.json`
  - `prototypes.json`
  - Threshold configuration


---

## Windowing Invariants (MVP)

- `length_frames = 16`
- `stride_frames = 5`
- `fps_nominal = 15`
- Windowing is internal to `gesture_classifier`
- If `T < length_frames`, emit reject outcome
- FPS mismatches must result in either resampling or reject outcome
- Windowing parameters must be logged for reproducibility


---

## Capture-Level Aggregation Policy (MVP)

1. Segment bounded `(T, D)` tensor into windows.
2. For each window:
   - Compute embedding
   - Compute cosine similarity to class prototypes
   - Apply reject criteria
3. Aggregate only accepted windows:
   - If no windows accepted → reject
   - Otherwise compute mean class scores across accepted windows
   - Normalize to probability distribution


---

## Outputs

- Exactly one A3CPMessage per bounded capture
- `classifier_output`: `Dict[str, float]` mapping intent → confidence
- `"unknown"` MUST be included in every output

### Reject Rule

- If capture rejected:
  - `"unknown": 1.0`
  - All other intents: `0.0`

### Accept Rule

- `"unknown": 0.0`
- Remaining intents normalized to sum to `1.0`

Ranking is derived downstream by sorting the distribution.

All per-window details and reject reasons are written to `inference_trace.jsonl` keyed by `record_id`.


---

## CARE Integration

- **Upstream:** Receives bounded feature artifacts from `landmark_extractor`
- **Downstream:** Emits schema-compliant distribution to `input_broker`
- **Role:** Provides gesture-based intent distribution for multimodal fusion
- **Model Source:** Loads per-user artifacts from `model_registry`
- No public endpoint required for MVP


---

## Functional Requirements

- F1. Accept bounded landmark feature artifacts
- F2. Perform internal windowing and scoring
- F3. Aggregate window scores deterministically
- F4. Emit exactly one schema-valid A3CPMessage per capture
- F5. Include `"unknown"` in every output
- F6. Log per-window inference traces
- F7. Support manual retraining
- F8. Use versioned model artifacts


---

## Non-Functional Requirements

- NF1. Inference latency per capture <300ms under demo load
- NF2. Model artifacts must be versioned and immutable
- NF3. Full retrainability from stored features
- NF4. Schema validation before downstream propagation
- NF5. Concurrent per-user model caching supported
- NF6. Deterministic inference given identical inputs
- NF7. Audit-compliant logging


---

## Model Versioning & Cache Consistency (MVP)

- Each trained model must have a monotonic `model_version`
- `model_version` must be included in:
  - Emitted A3CPMessage
  - `inference_trace.jsonl`
- Model artifacts are immutable once written
- Cache refresh must use atomic swap
- Mixed-version inference within a capture is not permitted


---

## Developer(s)

Unassigned


---

## Priority

High


---

## SCHEMA COMPLIANCE SUMMARY

This module emits valid `A3CPMessage` records containing:

- `modality = "gesture"`
- `classifier_output`: `Dict[str, float]`
- `"unknown"` key always present
- `model_ref` and `encoder_ref` included

Detailed window-level scoring remains in `inference_trace.jsonl`.
