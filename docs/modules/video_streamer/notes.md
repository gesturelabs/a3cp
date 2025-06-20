# Developer Notes: video_streamer

## 1. Design Rationale

The `video_streamer` module is responsible for capturing real-time visual input from the user's camera and converting it into structured gesture data via landmark extraction. It operates as a session-oriented orchestrator that manages the video feed, extracts pose/body/hand/face landmarks using MediaPipe Holistic, and stores labeled data for training or evaluation. It does **not** perform inference directly; instead, it may forward extracted data to the `gesture_classifier` module for real-time classification.

Key architectural decisions:

- **Modular pipeline design**: `video_streamer` includes three key submodules:
  - `CameraFeedWorker` handles real-time video capture
  - `LandmarkExtractor` performs MediaPipe Holistic inference on frames
  - `RecordingPipeline` serializes the extracted landmarks with metadata to disk

- **Dedicated visual stream handling**: This module is fully decoupled from audio capture. All audio-related logic resides in the separate `audio_streamer` module. This allows for distinct schemas, processing, and independent scaling of each modality.

- **Training-first pipeline**: All visual recordings are treated as structured training data. In real-time sessions, landmark extraction runs continuously, regardless of whether inference is invoked, ensuring data continuity for later learning.

- **Inference-agnostic design**: Inference is delegated to the `gesture_classifier`, which allows the video streamer to remain stateless with regard to model identity, confidence thresholds, or prediction outputs.

- **Session-integrity tagging**: All outputs include consistent session identifiers, timestamps, intent labels, and pseudonyms. This ensures reproducibility and full audit trail traceability.

- **Support for contextual modules**: The video streamer may host additional observers (e.g., object or scene classifiers) that process the same camera frames in parallel to landmark extraction, enabling context-aware tagging without storing raw video.

Rejected alternatives:
- Combining video and audio streamers into a unified module was rejected due to diverging schemas, dependencies, and processing paths.
- Allowing video to be recorded without landmark extraction was ruled out due to privacy, storage, and compute constraints.
- Embedding inference inside the streamer was avoided to maintain clean separation of responsibilities and allow easy model-swapping in downstream modules.

The design prioritizes modularity, traceability, schema conformance, and audit-safe session capture.

---

## 2. Open Questions

- Should this module support multi-camera setups (e.g., caregiver + user views)?
- Is frame buffering needed in `CameraFeedWorker`, or should it drop frames under load?
- Should the MediaPipe pipeline support adjustable confidence thresholds per user?
- Can landmark extraction be toggled on/off dynamically for performance tuning?
- How do we cleanly handle backpressure if the recording pipeline or disk stalls?
- Should the system support auxiliary frame consumers (e.g., object classifiers)? How are resource limits and thread safety managed if multiple submodules access the camera feed?


---

## 3. Known Issues / Risks

- Device access varies by OS and can cause permission or indexing inconsistencies.
- Landmark extraction may crash or freeze on edge cases (e.g., missing body parts, lighting).
- If frame rates are too low, gestures may be misrepresented or missed.
- If session metadata is missing or malformed, recordings may be rejected by schema validators.
- Unbounded memory usage in queues or buffers could cause session crashes.

---

## 4. Development TODOs

- [ ] `CameraFeedWorker` implementation with async or threaded stream
- [ ] `LandmarkExtractor` pipeline using MediaPipe Holistic
- [ ] `RecordingPipeline` with schema v1.0 conformance
- [ ] Sample `.parquet` writer with pseudonym/session metadata
- [ ] Logging integration across all submodules
- [ ] Graceful fallback if no camera is detected
- [ ] Dev/test mode for running with sample video
- [ ] Add streaming hooks to `gesture_classifier` (optional)
- [ ] UI integration for camera selector and capture start

---

## 5. Edge Case Handling

- If no camera is detected, the system should log a warning and disable capture gracefully.
- If MediaPipe fails to extract valid landmarks, the frame should be dropped with a logged error.
- If disk write fails (e.g., full disk), fallback policy must determine whether to retry, halt, or discard.
- Timestamps should be synchronized to a session-start reference to avoid cross-user clock drift.
- Intent label may be entered post-hoc but must be validated before record finalization.
- Partial-body capture is expected (e.g., feet or hands may be out of frame). Each frame must store landmark confidence, and downstream modules must tolerate missing keypoints.

---

## 6. Integration Notes

- **To Gesture Classifier**: Sends landmark vectors for optional live classification via event or message queue.
- **To Recording Pipeline**: Pushes frame-level landmarks with timestamps, session metadata, and labeling.
- **From Session Controller**: Receives session ID, user pseudonym, intent label, and consent flags.
- **From Camera Config UI**: Accepts camera index, resolution, and FPS preferences.
- **Output Format**: Must serialize records to `RawActionRecord` v1.0 or higher, optionally in `.parquet` or `.jsonl`.
- **To Object Classifier (future)**: May expose a shared frame bus for real-time contextual analysis. No raw video is saved; classifiers must act live on per-frame basis.


---

## 7. References

- [`SCHEMA_REFERENCE.md`](../../schemas/SCHEMA_REFERENCE.md) — current field definitions for `RawActionRecord`
- [`video_streamer_architecture.drawio`](./diagrams/video_streamer_architecture.drawio) — submodule interaction diagram
- [`gesture_classifier/notes.md`](../gesture_classifier/notes.md) — classification interface integration
- A3CP Design Document v3 – Section 6.2 (Streamer & Capture Stack)
- A3CP CARE Loop Overview — high-level data and feedback flow
