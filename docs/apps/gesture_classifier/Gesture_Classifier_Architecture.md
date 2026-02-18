# Module: gesture_classifier_2

## Internal Model Architecture

### Overview

The `gesture_classifier` uses a lightweight, per-user temporal model optimized for low-data, low-latency inference over **bounded gesture captures**.

The architecture is designed for:

- Deterministic replay from stored feature artifacts
- Conservative reject behavior
- Few-shot stability
- Edge portability
- Strict schema compliance

Streaming semantics are not part of the MVP. Windowing is internal to the module, and aggregation occurs at the capture level. Exactly one A3CPMessage is emitted per bounded capture.

---

### Input Representation

Inference operates on a **bounded landmark feature tensor `(T, D)`** referenced by `raw_features_ref`.

The module internally segments this tensor into fixed-length windows for scoring.

**Internal Window Parameters (MVP)**

- **Window Length**: 16 frames (~1.1s at 15 FPS nominal)
- **Stride**: 5 frames
- Windows are used internally for scoring only; aggregation produces a single capture-level output.

**Input Features per Frame**

- Person-centered, normalized 2D landmark coordinates (x, y)
- Visibility mask values
- Per-landmark 2D velocities
- Reduced facial landmark subset

**Excluded Features (MVP)**

- Z-coordinate (depth)
- Acceleration vectors
- Hand joint angles

**Upstream Preprocessing (Versioned)**

Performed by `landmark_extractor` and recorded in metadata:

- Torso-centered translation
- Scale normalization (e.g., shoulder width)
- Light temporal smoothing prior to velocity computation

All preprocessing versions must be recorded and logged for reproducibility.

---

### Windowing Invariants (MVP)

- `length_frames = 16`
- `stride_frames = 5`
- `fps_nominal = 15`
- Windowing is performed internally over the bounded `(T, D)` tensor.
- If `T < length_frames`, the capture is treated as insufficient evidence and the module emits reject outcome.
- If FPS metadata deviates materially from `fps_nominal`, the classifier must either:
  - Resample to nominal rate (if implemented), or
  - Emit reject outcome with reason logged.
- Windowing parameters must be logged in `inference_trace.jsonl` for deterministic replay.

---

### Encoder

- **Architecture**: Small Temporal Convolutional Network (TCN)
- **Design Goal**: Low capacity to reduce overfitting in few-shot settings
- **Embedding Size**: 32–64 dimensions (small by design)
- **Training Regime**: Per-user training from scratch (MVP)
- **Export Format**: PyTorch → ONNX

The encoder transforms each `[16, D]` window into a fixed-length embedding vector.

---

### Classifier Head

- **Type**: Prototype-based classifier
- **Mechanism**:
  - Compute centroid embedding per intent class
  - Compute cosine similarity between window embedding and class prototypes
  - Convert similarities into class scores
- **Unknown Handling**: Not a trained class; produced via reject logic

Prototype artifacts are stored separately from encoder weights.

---

### Capture-Level Aggregation Policy (MVP)

1. Segment bounded `(T, D)` tensor into windows.
2. For each window:
   - Compute embedding
   - Compute cosine similarity to class prototypes
   - Apply per-window reject criteria
3. Aggregate only accepted windows:
   - If `accepted_window_count == 0` → reject capture
   - Otherwise compute mean class scores across accepted windows
   - Normalize to probability distribution
4. Emit exactly one A3CPMessage per bounded capture.
5. Write full per-window scores and rejection reasons to `inference_trace.jsonl` keyed by `record_id`.

---

### Reject / Unknown Policy

Reject operates at two levels:

#### Per-window Reject Criteria

- Activity score below threshold
- Top confidence below threshold (τ)
- Margin between top-1 and top-2 below minimum (m)

#### Capture-level Reject Rule

- If no windows pass reject criteria → output reject

Schema rule:

- `"unknown"` MUST be present in `classifier_output`
- If rejected:
  - `"unknown": 1.0`
  - All other intents: `0.0`
- If accepted:
  - `"unknown": 0.0`
  - Remaining intents normalized to sum to `1.0`

Thresholds are global in MVP and configurable via model metadata.




### Signal Quality Gates (MVP)

In addition to confidence-based reject criteria, the classifier must enforce deterministic signal quality constraints to prevent unstable or spurious predictions.

A capture is rejected (`"unknown"`) if any of the following conditions hold:

1. **Low Landmark Visibility**
   - Mean visibility score across keypoints within accepted windows falls below `min_visibility_threshold`.
   - Visibility is computed as the mean of upstream visibility masks for tracked keypoints.

2. **Excessive Missing Keypoints**
   - The ratio of missing or zeroed keypoints within a window exceeds `max_missing_ratio`.

3. **Insufficient Motion Energy**
   - Mean motion energy across accepted windows falls below `min_motion_energy_threshold`.
   - Motion energy is computed as the mean L2 norm of per-keypoint velocity vectors.

4. **Dimensionality Mismatch**
   - `(T, D)` tensor dimensionality does not match `model_metadata.dims`.

5. **Insufficient Valid Windows**
   - Total accepted windows after windowing and per-window reject < `min_valid_windows`.

All threshold values must be stored in `model_metadata.json` and versioned with `model_version`.

All signal-quality reject reasons must be logged in `inference_trace.jsonl` keyed by `record_id`.

Signal quality enforcement is deterministic and must produce identical results given identical inputs and model metadata.


### Emission Policy

- Exactly one A3CPMessage per bounded capture
- No per-window emission
- No streaming cadence guarantees
- No event latching or cooldown logic
- Downstream modules handle temporal reasoning across captures

---

### Training Policy (MVP)

- Manual retrain only (user-triggered)
- Retrains encoder and recomputes prototypes
- No automatic incremental prototype updates
- Full landmark feature artifacts stored for retraining
- All training runs produce a new `model_version`

---

### Model Artifact Structure

Per user:

- `encoder.onnx`
- `label_map.json`
- `prototypes.json`
- `model_metadata.json` (preprocessing_version, normalization_version, timestamp, thresholds)

Artifacts are versioned and stored in `model_registry`.

---

### Model Versioning & Cache Consistency (MVP)

- Each trained model must have a monotonically increasing `model_version`.
- `model_version` must be included in:
  - Emitted A3CPMessage
  - `inference_trace.jsonl`
  - `model_metadata.json`
- Model artifacts are immutable once written.
- Models must be loaded as immutable objects keyed by `(user_id, model_version)`.
- Cache refresh during retrain must use atomic swap.
- Mixed-version inference within a single bounded capture is not permitted.

This ensures deterministic replay and prevents race-condition inconsistencies.

---

### Determinism Requirements

Given:

- Identical `(T, D)` feature tensor
- Identical preprocessing version
- Identical `model_version`
- Identical windowing parameters

Inference must be reproducible within floating-point tolerance.

---

### Deployment Strategy

- Server-side inference for MVP
- Thin browser client
- Target edge deployment: Jetson Orin Nano
  - ONNX runtime required
  - TensorRT optional optimization layer
- Multiple concurrent users supported via per-user in-memory model caching
- All artifacts immutable and versioned

---

### Architectural Priorities

- Determinism
- Few-shot stability
- Conservative false-positive control
- Auditability
- Edge portability
- Incremental extensibility
