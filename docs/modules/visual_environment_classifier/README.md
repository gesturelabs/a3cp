# Module: visual_environment_classifier

## Purpose
Classifies the user's physical environment (e.g., kitchen, classroom, bedroom, store) in real time using visual input from the camera stream.

## Why It Matters
Scene awareness enables more accurate disambiguation of user intents. Knowing whether the user is at home, in public, or in a specific functional space improves the relevance and safety of AAC outputs and CARE loop decisions.

## Responsibilities
- Subscribe to live video frames from `camera_feed_worker`
- Run a visual environment classifier on each frame (e.g., CNN-based model)
- Output structured predictions with confidence scores
- Tag each prediction with timestamp and frame/session metadata
- Log classification output for auditing and analysis

## Not Responsible For
- Capturing or buffering video frames (done by `camera_feed_worker`)
- Storing raw video or user images
- Landmark extraction or gesture analysis
- Clarification logic or final output decisions

## Inputs
- Real-time video frames (`np.ndarray`) from `camera_feed_worker`
- Optional frame metadata: `session_id`, `frame_id`, `timestamp`, `device_id`

## Outputs
- `environment_label`: e.g., `"kitchen"`, `"bedroom"`, `"store"`, `"outdoors"`
- `confidence_score`: Float in [0.0, 1.0]
- `timestamp`: Frame timestamp (synced with camera feed)
- `context.flags`: Optional contextual tags (e.g., `is_public`, `is_cooking_area`)
- `audit_metadata`: Includes model version, input hash, source module

## CARE Integration
- **Upstream**: Receives frames from `camera_feed_worker` via shared interface
- **Downstream**: Supplies context to `confidence_evaluator`, `output_planner`, or `clarification_planner`
- **Audit**: Logs each classification decision with reproducible metadata

## Functional Requirements
- F1. Must classify scenes using fixed known categories
- F2. Must operate on live frame stream, not just static images
- F3. Must emit predictions in schema-compliant JSON or dict format
- F4. Must support configurable model checkpoint and threshold

## Non-Functional Requirements
- NF1. Average inference time per frame <100ms on CPU
- NF2. Must not block other consumers of the camera feed
- NF3. Must log all predictions for later audit

## Developer(s)
Osama

## Priority
Medium

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
