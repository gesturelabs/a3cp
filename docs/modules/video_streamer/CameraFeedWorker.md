# Submodule: CameraFeedWorker

## Purpose
Captures frames from a local video input device (e.g., webcam) and streams them to downstream modules in real time.
Acts as the source for all video-derived data such as landmarks, classification, and recording.

## Responsibilities
- Open and manage access to the selected video device
- Stream video frames at the configured resolution and frame rate
- Timestamp each frame accurately (monotonic clock or synchronized UTC)
- Forward frames to downstream consumers (e.g., LandmarkExtractor)
- Signal availability/failure of video input to orchestrating module

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
- Session metadata (optional but forwardable):
  - `session_id`, `user_id`, `pseudonym`

## Outputs
- Timestamped video frames (e.g., OpenCV `np.ndarray`)
- Stream metadata (e.g., `frame_id`, `timestamp`, `device_id`)
- Error signals (e.g., device unavailable)

## Runtime Considerations
- Should support threaded or asynchronous capture to avoid blocking I/O
- Must expose a clean interface for downstream modules to subscribe or poll
- Device failure must raise recoverable errors (e.g., camera unplugged)
- Should allow graceful shutdown and restart across sessions

## Open Questions
- Should this support switching between multiple cameras in-session?
- Should frame buffering or skipping be handled here, or by downstream modules (e.g., to drop frames during backlog)?
- How are capture timestamps synchronized with audio streams or system clock?
- Is there value in exposing a preview stream (e.g., for debugging or UI feedback)?

## Notes
- This module is designed to support reproducible data capture for training and analysis.
- All downstream recording assumes that frame timestamps are reliable and deterministic.
- The current system adheres to `RawActionRecord` schema v1.0 (handled downstream).
