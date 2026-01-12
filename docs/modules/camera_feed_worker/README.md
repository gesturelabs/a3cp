# Submodule: camera_feed_worker

### Deprecate superseded by apps/module


## Purpose
Captures frames from a local video input device (e.g., webcam) and streams them to downstream modules in real time.
Acts as the source for all video-derived data such as landmarks, classification, and recording.

| Field             | Value                  |
|------------------|------------------------|
| **Module Name**  | `camera_feed_worker`   |
| **Module Type**  | `worker`               |
| **Inputs From**  | `session_manager` |
| **Outputs To**   | `landmark_extractor`, `schema_recorder` |
| **Produces A3CPMessage?** | ❌ No |

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
- Optional metadata (used for downstream schema attachment): session_id, user_id. These fields do not influence video capture, but are useful for tagging frames in downstream logs.


`camera_feed_worker` receives its runtime configuration from the `session_manager`.

Configuration includes:

- `device_id` or camera index
- Target resolution (e.g., 640x480)
- Target FPS (e.g., 30)

These values may be selected by user profile, test mode, or default fallback,
but are always injected at runtime via session configuration.

This ensures:
- Separation of capture and config logic
- Statelessness and reentrancy
- Compatibility with session-based resource control


## Outputs
- Timestamped video frames (e.g., OpenCV `np.ndarray`)
- Stream metadata (e.g., timestamp, device_id, optional stream_segment_id, frame_index) — conforms to Section 3.1
- Error signals (e.g., device unavailable, read failure)
This module does not emit schema-compliant messages directly. Instead, it produces raw video frames (np.ndarray) and basic metadata. Schema wrapping (e.g., into RawActionRecord or A3CPMessage) is performed downstream (e.g., by the LandmarkExtractor or SchemaRecorder).

## OUTPUT PAYLOAD FORMAT (internal)
This module emits video frames as OpenCV `np.ndarray` objects, along with metadata
used by downstream modules (e.g., `landmark_extractor`, `schema_recorder`).

Each frame is passed as a tuple or dict-like object with the following structure:


{
  "frame": <np.ndarray>,                 # Raw RGB or BGR image array
  "timestamp": <ISO 8601 string>,       # UTC timestamp of frame capture
  "device_id": <string>,                # Logical source ID for the video device
  "frame_index": <int, optional>,       # Frame number in sequence
  "stream_segment_id": <str, optional>, # Optional windowing ID
  "session_id": <str, optional>,        # Session identifier for downstream logs
  "user_id": <str, optional>            # Optional pseudonymous user ID
}

This format must be:
- Emitted via thread-safe queue or callback
- Interpreted by consumers for further processing or schema wrapping
- Synchronized using monotonic timestamps with millisecond resolution


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
- [ ] Define CameraFrameMetadata model aligned with A3CPMessage input structure (timestamp, device_id, modality="image", source="communicator", etc.)
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


-------------------------------------------------------------------------------
⚠ SCHEMA COMPLIANCE DISCLAIMER
-------------------------------------------------------------------------------

This module does **not** emit schema-compliant records (e.g., `A3CPMessage`).

It streams raw video frames and metadata. Schema wrapping is the responsibility
of downstream consumers such as `landmark_extractor` or `schema_recorder`.

Consumers must:
- Interpret the timestamp and ID metadata for alignment
- Insert schema-required fields (`modality="image"`, `source="communicator"`)
- Produce logs compatible with `SCHEMA_REFERENCE.md`


## References
- [`SCHEMA_REFERENCE.md`](../../schemas/SCHEMA_REFERENCE.md) — field definitions for video input records
- [`gesture_classifier/README.md`](../gesture_classifier/README.md) — for downstream consumer expectations
- [`camera_feed_architecture.drawio`](./diagrams/camera_feed_architecture.drawio) — architecture diagram (WIP)
- A3CP Design Doc v3 – Section 6.2 (Visual Stream Stack)
- MediaPipe Holistic documentation: https://developers.google.com/mediapipe/solutions/vision/holistic
