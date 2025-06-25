# Module: gesture_classifier

## Purpose
Classifies processed gesture vectors into structured intent candidates with confidence scores. This module enables gesture-based communication by transforming raw user gestures into interpretable predictions.

## Why It Matters
Gesture classification is the foundation of nonverbal intent inference in the A3CP system. By producing structured predictions from learned user-specific models, this module allows the CARE Engine to act on gestures with contextual precision. It supports adaptive interaction and contributes to improved communication responsiveness and trust.

## Responsibilities
- Accept pre-processed gesture input vectors and metadata
- Run inference using user-specific models and label encoders
- Return ranked intent candidates with associated confidence scores
- Serve `/api/gesture/infer/` via FastAPI (or other gateway)
- Validate all outputs against A3CPMessage schema
- Log all inferences to `inference_trace.jsonl` for auditing

## Not Responsible For
- Consent collection or input recording
- Fusion of gesture with other modalities (handled elsewhere)
- Clarification triggers or output rendering
- Model training orchestration or input pre-processing

## Inputs
- `gesture_vector`: Processed gesture landmarks (e.g., 3D or time series input)
- `user_id`, `session_id`, `timestamp`: Session metadata
- `modality` / `source` tags for traceability
- Internal references to per-user model (.h5) and encoder (.pkl)

## Outputs
- `intent_candidates`: Ranked list with intent labels and confidence scores
- A3CPMessage-compliant payload for downstream CARE modules
- Entry in `inference_trace.jsonl` (including model version, input ref, prediction)

## CARE Integration
- **Upstream**: Receives input from `gesture_recorder` or `landmark_extractor`
- **Downstream**: Sends structured predictions to `clarification_planner`, `confidence_evaluator`, or `CARE Engine`
- **API**: Serves `/api/gesture/infer/` using the unified A3CPMessage schema

## Functional Requirements
- F1. Accept gesture vectors from recording interface post-consent
- F2. Store gesture data in session-organized `.parquet` format
- F3. Train per-user LSTM using stored vectors and labels
- F4. Save model (`.h5`) and encoder (`.pkl`) to registry with metadata
- F5. Implement `/api/gesture/infer/` endpoint with A3CPMessage schema compliance
- F6. Return `intent_candidates` with confidence scores from model
- F7. Log all inferences to `inference_trace.jsonl`

## Non-Functional Requirements
- NF1. Inference latency must be <300ms per input
- NF2. All artifacts must be timestamped and versioned
- NF3. Models must be retrainable using the same pipeline
- NF4. All predictions must pass JSON schema validation
- NF5. System must support concurrent inference across users

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
