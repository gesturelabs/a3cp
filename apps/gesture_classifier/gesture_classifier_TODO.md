# gesture_classifier — MVP TODO Outline

## 1. Core Inference Pipeline

- [ ] Implement model artifact loader
  - [ ] Load `encoder.onnx`
  - [ ] Load `label_map.json`
  - [ ] Load `prototypes.json`
  - [ ] Validate SHA-256 hashes
- [ ] Implement per-user model cache (keyed by `(user_id, model_version)`)
- [ ] Enforce atomic cache swap on retrain

- [ ] Implement bounded feature loading from `raw_features_ref`
  - [ ] Validate tensor shape `(T, D)`
  - [ ] Validate dims match model metadata
  - [ ] Enforce max T limit (DoS guard)

- [ ] Implement internal windowing
  - [ ] `length_frames = 16`
  - [ ] `stride_frames = 5`
  - [ ] Handle `T < 16` → reject
  - [ ] Log window metadata for trace

- [ ] Implement encoder inference (ONNX runtime)
- [ ] Implement prototype cosine similarity scoring
- [ ] Convert similarities → normalized distribution

- [ ] Implement per-window reject logic
  - [ ] Activity threshold
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
  - [ ] Reject reason (if any)
- [ ] Log:
  - [ ] `record_id`
  - [ ] `model_version`
  - [ ] `preprocessing_version`
  - [ ] Windowing parameters
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
- [ ] Validate feature dimensionality against metadata


---

## 7. Testing

- [ ] Unit tests: windowing logic
- [ ] Unit tests: reject behavior
- [ ] Unit tests: aggregation math
- [ ] Unit tests: `"unknown"` distribution rule
- [ ] Unit tests: schema validation
- [ ] Unit tests: cache swap correctness
- [ ] Integration test: end-to-end bounded capture → A3CPMessage


---

## 8. Documentation

- [ ] Update module spec (finalized)
- [ ] Document windowing invariants
- [ ] Document reject policy
- [ ] Document aggregation method
- [ ] Document deterministic replay requirements


---

## 9. Edge Readiness (Optional for MVP)

- [ ] Validate ONNX runtime on Jetson Orin Nano
- [ ] Benchmark inference time on target hardware
- [ ] Evaluate TensorRT optimization (deferred if needed)
