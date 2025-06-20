# Submodule: LandmarkExtractor

## Purpose
Processes incoming video frames to extract human pose, face, and hand landmarks using the MediaPipe Holistic model.
It acts as a transformer that converts raw visual input into structured feature vectors usable for training and inference.

## Responsibilities
- Initialize and configure the MediaPipe Holistic model
- Process each incoming frame and extract:
  - Pose landmarks
  - Hand landmarks (left and right)
  - Facial landmarks (optional or configurable)
- Timestamp each landmark set
- Forward extracted landmarks to:
  - `RecordingPipeline` for serialization
  - `gesture_classifier` for inference (if model is available and active)

## Not Responsible For
- Frame capture (handled by `CameraFeedWorker`)
- File I/O or schema-compliant writing
- User intent handling or classification logic
- Inference model evaluation (delegated to `gesture_classifier`)

## Inputs
- Timestamped video frames (e.g., OpenCV `np.ndarray`)
- Configuration parameters (e.g., which body parts to extract)
- Session metadata for context (e.g., session ID)

## Outputs
- Structured landmark vectors (e.g., dict of normalized coordinates)
- Extraction metadata (e.g., confidence scores, frame ID, timestamp)
- Forwarded landmark data to `RecordingPipeline`
- Optional parallel stream to `gesture_classifier` if inference is enabled

## Runtime Considerations
- MediaPipe Holistic can be CPU or GPU accelerated; performance tuning may be needed
- Model warmup time and frame skipping should be handled gracefully
- Must enforce output consistency across frames (e.g., missing hand landmarks handled as `None`)
- Should allow filtering or downsampling of output if performance is degraded

## Open Questions
- Should landmark extraction be performed for all body parts at once, or allow modular control (pose only, hands only)?
- How are failed frames (e.g., no person detected) represented downstream?
- Should confidence scores be used to filter low-quality frames?
- How are landmark vectors formatted — flat list, structured dict, or per-frame schema object?
- Should it report processing latency for performance monitoring?

## Notes
- This module currently uses MediaPipe Holistic vX.X (verify at implementation)
- All extracted data is passed downstream but not persisted directly
- It must maintain temporal alignment with the source frames and metadata
- Output is expected to comply with schema v1.0 for `RawActionRecord` (as consumed by `RecordingPipeline`)
