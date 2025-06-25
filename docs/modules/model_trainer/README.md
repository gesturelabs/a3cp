# Module: model_trainer

## Purpose
The `model_trainer` module builds per-user, modality-specific machine learning models using validated, labeled input data. It processes gesture vectors, audio features, or other time-aligned inputs and outputs versioned model artifacts with associated metadata.

## Why It Matters
This module enables adaptive learning in A3CP. Without personalized models, intent classification performance would degrade across diverse users and contexts. Training ensures tailored, accurate inference aligned with each user's communication patterns.

## Responsibilities
- Accept training requests with `user_id`, `modality`, and configuration
- Load labeled data from prior sessions for the given user and modality
- Apply modality-specific preprocessing (e.g., keyframe extraction, MFCC conversion)
- Train a classifier model using the configured algorithm and parameters
- Serialize:
  - Model artifact (e.g., `.h5`, `.onnx`, `.gguf`)
  - Label encoder (e.g., `.pkl`)
- Register the training outcome in the `model_registry`
- Log training metadata for audit, reproducibility, and debugging

## Not Responsible For
- Real-time inference (handled by classifiers)
- Clarification, fusion, or fallback logic
- Memory tracking or CARE-specific decision logic
- UI or visualization during training

## Inputs
- `user_id`: globally unique identifier (UUID or string)
- `modality`: one of `"gesture"`, `"sound"`, `"speech"`
- `labeled_training_data`: pre-cleaned input-label pairs
- `session_metadata`: timestamps, labeler info, modality version
- `training_config`: model type, architecture, hyperparameters, feature set

## Outputs
- `trained_model_artifact`: versioned model file (e.g., `gesture_model_user123_v1.h5`)
- `label_encoder`: serialized label mapping (e.g., `label_encoder_user123_v1.pkl`)
- `model_metadata_entry`: dict with user, modality, version, config summary
- `training_log_entry`: full training record (sample count, timestamp, metrics, outcome)

## CARE Integration
- Output models are referenced by `/api/infer/` during real-time inference
- Registry entries are used to locate the correct model for each session

## Functional Requirements
- FR1. Accept `user_id`, `modality`, and load corresponding labeled dataset
- FR2. Preprocess input data per modality and validate schema
- FR3. Train model with configured hyperparameters and architecture
- FR4. Save model and label encoder to versioned, user-tagged paths
- FR5. Log training outcome to model registry with schema-compliant entry
- FR6. Generate structured log with config, metrics, and timing

## Non-Functional Requirements
- NF1. Must support reproducible runs (e.g., controlled seed)
- NF2. Should train in under 30s for typical batch size (<1000 samples)
- NF3. Must validate inputs and schema before proceeding
- NF4. All outputs must be versioned and written atomically
- NF5. Errors must return structured JSON logs with tracebacks
- NF6. Compatible with CPU-only environments

## Developer(s)
Unassigned

## Priority
High – required for personalized CARE inference

## Example Filenames
- `gesture_model_user123_v3.h5`
- `label_encoder_user123_v3.pkl`
- `training_log_user123_v3.json`

## Open Questions
- Do we allow multi-session or merged training sets?
- Is there a default model to fall back on when user data is sparse?
- Should we version the encoder format and feature extraction method?
- Will we need support for model export formats like `.onnx` or `.tflite`?
