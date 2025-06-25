# Submodule: camera_feed_worker

## Purpose
Captures frames from a local video input device (e.g., webcam) and streams them to downstream modules in real time.
Acts as the source for all video-derived data such as landmarks, classification, and recording.

## Responsibilities
- Open and manage access to the selected video device
- Stream video frames at the configured resolution and frame rate
- Timestamp each frame accurately (monotonic or synchronized clock)
- Forward frames to downstream consumers (e.g., `LandmarkExtractor`)
- Signal availability/failure of video input to orchestrating modules

## Not Responsible For
- Landmark extraction or classification
- File I/O or schema-compliant recording
- Inference or decision-making logic
- Intent capture or session coordination

## Inputs
- Configuration parameters:
  - `device_id` (e.g., `/dev/video0`, index 0)
  - Target resolution (e.g., 640x480)
  - Target FPS (e.g., 30)
- Optional metadata (forwarded if available):
  - `session_id`, `user_id`, `pseudonym`

## Outputs
- Timestamped video frames (e.g., OpenCV `np.ndarray`)
- Stream metadata (e.g., `frame_id`, `timestamp`, `device_id`)
- Error signals (e.g., device unavailable, read failure)

## Runtime Considerations
- Should support threaded or asynchronous capture to avoid blocking I/O
- Must expose a clean interface (e.g., iterator, callback, queue) for downstream modules
- Camera failure must raise recoverable exceptions and emit diagnostic logs
- Should allow graceful shutdown/restart across sessions

---

## Design Rationale
The `camera_feed_worker` was split out of the former `video_streamer` module to enforce separation of concerns. This submodule is solely responsible for robust, real-time frame capture from a video device.

### Architectural decisions:
- **No side effects**: This module performs no inference, transformation, or disk writes.
- **Deterministic timestamps**: Frames are timestamped immediately after capture for alignment with audio or event logs.
- **Upstream agnostic**: The source can be a webcam, virtual camera, or test stream; the interface remains uniform.
- **Resilience-first**: Emphasis on handling hardware failures, disconnections, or high-latency conditions gracefully.

---

## Edge Case Handling
- If no video device is detected, the module must log and fail gracefully.
- If the device is busy or permissions are denied, fallback behavior should be defined (e.g., retry or abort).
- Frame reads may occasionally return `None`; these should be skipped with logs.
- Timestamps must remain monotonic to preserve event ordering even during frame skips or lag.
- Frame dropping under high load should be tunable (e.g., max buffer size, skip strategy).
- Should support a simulated camera mode for dev/test (e.g., looping a sample video file).

---

## Known Issues / Risks
- Hardware indexing may vary across platforms (e.g., `/dev/video0` vs index `1`)
- Frame read latency can spike on some systems when resolution is changed dynamically
- Threading or GIL-related capture bugs are possible if OpenCV is not isolated
- In environments like Streamlit, `cv2.VideoCapture()` may hang or fail silently — Django/WSGI likely avoids this
- MediaPipe pipeline compatibility depends on input frame format; pre-checks may be required

---

## Development TODOs
- [ ] Implement threaded frame capture with `cv2.VideoCapture`
- [ ] Expose a generator/queue interface for downstream pull or push
- [ ] Add logging for stream start/stop, errors, and dropped frames
- [ ] Add schema stub for emitted frame metadata (for downstream use)
- [ ] Implement test camera fallback using pre-recorded sample
- [ ] Add `dev_mode` CLI or config toggle
- [ ] Validate device availability on startup

---

## Open Questions
- Should this support dynamic camera switching during a session?
- Should timestamp synchronization with audio use wall clock or sync pulse?
- Should frame skip/backpressure be handled here or downstream?
- Is there value in optionally saving preview snapshots for debugging?
- Do we need an internal FPS monitor to detect drift?

---

## Integration Notes
- **To `LandmarkExtractor`**: Frame is passed directly via shared queue or callback.
- **To `schema_recorder`**: Metadata may be attached downstream for logging.
- **From config manager**: Device index, resolution, and FPS may be injected via session config.
- **Output schema**: Frames are raw (`np.ndarray`) with metadata; downstream schema validation applies (e.g., `RawActionRecord`).

---

## References
- [`SCHEMA_REFERENCE.md`](../../schemas/SCHEMA_REFERENCE.md) — field definitions for video input records
- [`gesture_classifier/README.md`](../gesture_classifier/README.md) — for downstream consumer expectations
- [`camera_feed_architecture.drawio`](./diagrams/camera_feed_architecture.drawio) — architecture diagram (WIP)
- A3CP Design Doc v3 – Section 6.2 (Visual Stream Stack)
- MediaPipe Holistic documentation: https://developers.google.com/mediapipe/solutions/vision/holistic
