# Module: landmark_extractor

## legacy...see module for updates

| Field                  | Value                                      |
|------------------------|--------------------------------------------|
| **Module Name**        | `landmark_extractor`                       |
| **Module Type**        | `classifier`                               |
| **Inputs From**        | `camera_feed_worker`                       |
| **Outputs To**         | `gesture_classifier`, `schema_recorder`    |
| **Produces A3CPMessage?** | ✅ Yes (via `raw_features_ref`)         |

-------------------------------------------------------------------------------
✅ SCHEMA COMPLIANCE SUMMARY
-------------------------------------------------------------------------------

This module emits schema-compliant records using `A3CPMessage` format with:

- `modality = "image"`, `source = "communicator"`
- `timestamp`, `user_id`, `session_id`, `device_id`
- `raw_features_ref`: reference to external vector file (e.g., `.parquet`)
- `vector_version`: version of encoding used (e.g., `"landmark_v2.1"`)

All production logs must use `raw_features_ref` with:
- Content hash
- Feature dimensionality
- Encoding type
- External URI path

Inline `vector` output is deprecated and may be used only in test mode.


## Purpose
The `landmark_extractor` module processes timestamped video frames from the `camera_feed_worker` and uses the MediaPipe Holistic model to extract body, hand, and face landmarks. These structured vectors are passed to the `gesture_classifier` for inference and to the `schema_recorder` for logging and training purposes.

## Why It Matters
This module transforms raw visual input into structured, interpretable features that are essential for understanding nonverbal communication in A3CP. It enables both real-time intent inference and long-term model improvement through labeled gesture data.

## Responsibilities
- Initialize and configure the MediaPipe Holistic model (CPU/GPU).
- Extract pose, hand (left/right), and facial landmarks from each frame.
- Normalize and timestamp each landmark vector.
- Package outputs as structured feature vectors.
- Forward results to:
  - `gesture_classifier` for live inference.
  - `schema_recorder` for training data logging and audit.

## Not Responsible For
- Capturing raw frames (handled by `camera_feed_worker`).
- File I/O, consent, or user intent labeling.
- ML classification or decision-making.
- Schema enforcement or downstream processing.

## Inputs
- Video frame (`np.ndarray`).
- Frame-level metadata (`timestamp`, `session_id`, `user_id`, `device_id`).
- Configuration options (e.g., which landmarks to extract).

## Outputs
- Structured landmark vectors:
  - Flat or hierarchical dicts with normalized 2D/3D coordinates.
  - May include confidence scores and missing landmark indicators.
- Metadata attached:
  - `timestamp`, `frame_id`, `modality`, `source`, `vector_version`.
- Passed to:
  - `gesture_classifier` for intent prediction.
  - `schema_recorder` for logging into session training records.

## Output Format (Feature Vector Record as A3CPMessage)
{
  "schema_version": "1.0.0",
  "record_id": "uuid4-here",
  "user_id": "elias01",
  "session_id": "sess_2025-07-01_elias01",
  "timestamp": "2025-07-01T13:21:11.654Z",
  "modality": "image",
  "source": "communicator",
  "device_id": "cam_01",
  "vector_version": "landmark_v2.1",
  "raw_features_ref": {
    "uri": "/data/elias01/frame_00023.parquet",
    "hash": "sha256:abcdef1234567890...",
    "encoding": "landmark_v2.1",
    "dims": 128,
    "format": "parquet"
  }
}


## CARE Integration
- **Feeds**: `gesture_classifier` during inference sessions.
- **Logs to**: `schema_recorder` for feedback-driven model refinement.
- **Supports**: CARE Engine by enabling gesture-based intent recognition.
- **Formats**: Output compatible with `RawActionRecord` schema.

## Functional Requirements
- F1. Must extract 2D/3D landmark vectors from each input frame.
- F2. Must support configurable landmark subsets (e.g., pose only).
- F3. Must forward extracted vectors to both inference and recording pipelines.
- F4. Must annotate each vector with frame metadata.

## Non-Functional Requirements
- NF1. Must maintain low latency (<100ms/frame on CPU).
- NF2. Must degrade gracefully if some landmarks are missing.
- NF3. Must ensure stable output structure across frames and sessions.
- NF4. Must provide performance metrics for optional logging/debug.

## Runtime Considerations
- Holistic model initialization delay (warmup) must not block UI.
- Frame skipping or batch sampling strategies may be needed under load.
- Vectors with partial detections (e.g., occluded hands) must remain schema-valid.
- Confidence-based filtering should be available as a toggle.

## Open Questions
- Should confidence thresholds be user-configurable?
- Should we track failed frames for UI feedback or performance audit?
- Should vectors include landmark velocity/delta calculations?
- Is flat or hierarchical vector format more compatible with model training?

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
