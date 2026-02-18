# gesture_classifier — MVP TODO Outline (Revised for Universal Encoder Compatibility)

## 1. Core Inference Pipeline

- [ ] Implement model artifact loader
  - [ ] Load `encoder.onnx`
  - [ ] Load `encoder_metadata.json` (required)
    - [ ] Validate `feature_spec_id` matches input artifact
    - [ ] Read `embedding_dim`
    - [ ] Read `fps_nominal` (or `supports_variable_fps`)
    - [ ] Read `expects_length_frames` (fixed vs variable)
    - [ ] Read `normalization_version`, `smoothing_version`
  - [ ] Load `label_map.json`
  - [ ] Load `prototypes.json`
  - [ ] Validate SHA-256 hashes (all artifacts)
- [ ] Implement per-user model cache (keyed by `(user_id, model_version)`)
- [ ] Enforce atomic cache swap on retrain

- [ ] Implement bounded feature loading from `raw_features_ref`
  - [ ] Validate tensor shape `(T, D)`
  - [ ] Validate `feature_spec_id` present and matches `encoder_metadata.json`
  - [ ] Validate dims match `encoder_metadata.json` (expected `D`)
  - [ ] Enforce max T limit (DoS guard)
  - [ ] Log `feature_spec_id`, `normalization_version`, `smoothing_version` to trace

- [ ] Implement internal windowing
  - [ ] Resolve `length_frames` (default `16`, may be overridden by `encoder_metadata.json` if `expects_length_frames` differs)
  - [ ] Resolve `stride_frames` (default `5`)
  - [ ] Read `fps_estimate` from artifact metadata (required if available)
  - [ ] If `fps_estimate` differs from encoder `fps_nominal`:
    - [ ] Resample to `fps_nominal` OR reject (policy must be deterministic)
    - [ ] Log resampling/reject decision + method
  - [ ] Handle `T < length_frames` → reject
  - [ ] Log window metadata for trace

- [ ] Implement encoder inference (ONNX runtime)
- [ ] Implement prototype cosine similarity scoring
- [ ] Convert similarities → normalized distribution

- [ ] Implement per-window reject logic
  - [ ] Activity threshold
  - [ ] Tracking quality threshold (derived from visibility/missingness)
    - [ ] Reject window if missingness fraction > X OR mean visibility < Y
    - [ ] Log missingness stats + visibility stats per window
    - [ ] Record reject reason = `low_quality`
  - [ ] Top confidence threshold (τ)
  - [ ] Margin threshold (m)

- [ ] Implement capture-level aggregation
  - [ ] Aggregate accepted windows
  - [ ] Reject if none accepted
  - [ ] Normalize distribution
  - [ ] Ensure `"unknown"` key always present

- [ ] Emit exactly one A3CPMessage per capture
  - [ ] Validate schema before emit


---

## 2. Reject / Unknown Handling

- [ ] Implement capture-level reject rule
- [ ] Enforce distribution rule:
  - [ ] Reject → `"unknown": 1.0`, others 0.0
  - [ ] Accept → `"unknown": 0.0`, others sum to 1.0
- [ ] Ensure downstream ranking derivable via sort


---

## 3. Logging & Auditability

- [ ] Create `inference_trace.jsonl`
- [ ] Log per-window:
  - [ ] Embedding hash (optional)
  - [ ] Raw similarity scores
  - [ ] Quality metrics:
    - [ ] Missingness fraction
    - [ ] Mean visibility
  - [ ] FPS handling:
    - [ ] `fps_estimate`
    - [ ] `fps_nominal`
    - [ ] Resampling method OR reject flag
  - [ ] Reject reason (if any)
- [ ] Log:
  - [ ] `record_id`
  - [ ] `model_version`
  - [ ] `preprocessing_version`
  - [ ] `feature_spec_id`
  - [ ] `normalization_version`
  - [ ] `smoothing_version`
  - [ ] Windowing parameters (resolved `length_frames`, `stride_frames`)
- [ ] Ensure deterministic replay possible from trace + artifact


---

## 4. Model Versioning & Integrity

- [ ] Enforce immutable model artifacts
- [ ] Require monotonic `model_version`
- [ ] Verify artifact hash before load
- [ ] Prevent mixed-version inference within a capture


---

## 5. Performance & Determinism

- [ ] Ensure inference latency <300ms per capture (demo load)
- [ ] Add deterministic replay test (same input → same output)
- [ ] Add floating-point tolerance test


---

## 6. Security & Validation

- [ ] Validate artifact URI scheme (allowlist)
- [ ] Validate SHA-256 hashes before load
- [ ] Enforce maximum capture length (T limit)
- [ ] Validate feature dimensionality against `encoder_metadata.json`
- [ ] Reject incompatible `feature_spec_id`


---

## 7. Testing

- [ ] Unit tests: windowing logic
- [ ] Unit tests: FPS mismatch policy (resample or reject is deterministic)
- [ ] Unit tests: tracking quality gate (missingness/visibility thresholds)
- [ ] Unit tests: reject behavior
- [ ] Unit tests: aggregation math
- [ ] Unit tests: `"unknown"` distribution rule
- [ ] Unit tests: schema validation
- [ ] Unit tests: cache swap correctness
- [ ] Integration test: end-to-end bounded capture → A3CPMessage


---

## 8. Documentation

- [ ] Update module spec (finalized)
- [ ] Document windowing invariants (including resolved `length_frames` behavior)
- [ ] Document FPS mismatch policy (resample vs reject, deterministic)
- [ ] Document tracking quality gate thresholds + rationale
- [ ] Document reject policy
- [ ] Document aggregation method
- [ ] Document deterministic replay requirements


---

## 9. Edge Readiness (Optional for MVP)

- [ ] Validate ONNX runtime on Jetson Orin Nano
- [ ] Benchmark inference time on target hardware
- [ ] Evaluate TensorRT optimization (deferred if needed)
