# Module: landmark_visualizer

## Purpose
The `landmark_visualizer` module renders body pose, hand, and facial landmarks—either in real time or from recorded sessions—providing visual feedback for users, caregivers, and developers. It enhances transparency, enables debugging, and builds trust by showing exactly what the system “sees.”

## Why It Matters
Visualizing the detected landmarks helps identify calibration issues, ensures the correct body parts are tracked, and aids caregivers in validating input quality. It also supports documentation, review, and interface demonstrations without affecting the core inference pipeline.

## Responsibilities
- Render 2D/3D skeleton overlays based on MediaPipe-style landmark vectors.
- Support both:
  - **Live mode** (connected to `camera_feed_worker` + `landmark_extractor`), and
  - **Playback mode** (from stored gesture records).
- Display session metadata (user ID, timestamp, modality).
- Export annotated frames or sequences for feedback, documentation, or debugging.

## Not Responsible For
- Extracting landmarks (handled by `landmark_extractor`).
- Classification or inference (handled by `gesture_classifier`).
- Session management or I/O logic.
- Schema validation of inputs.

## Inputs
- `landmark_vectors`: structured outputs from MediaPipe or `landmark_extractor`.
- `session_metadata`: includes timestamp, user_id, session_id, modality.
- `raw_webcam_frames` (optional): for visual overlays behind skeleton.

## Outputs
- `rendered_overlay`: visualized landmarks (matplotlib/cv2/JS plotly/etc).
- `annotated_frame_exports`: still images or video clips for documentation.
- `playback_visual_feedback`: UI component for viewing gesture sequences.

## CARE Integration
- **Visualizes**: gesture input that feeds into `gesture_classifier`.
- **Used by**: developers and caregivers during training, debugging, or clarification.
- **Supports**: Human-in-the-loop workflows, especially in ambiguous sessions.
- **Does not participate in**: classification or output planning directly.

## Functional Requirements
- F1. Must accept MediaPipe-compatible landmark vectors (single or sequence).
- F2. Must render skeleton overlays with consistent keypoint mappings.
- F3. Must display timestamp and metadata alongside visuals.
- F4. Must support live and recorded modes.
- F5. Must allow export of annotated visuals (still or animated frames).

## Non-Functional Requirements
- NF1. Must support multiple display resolutions (e.g., 720p, 1080p).
- NF2. Must be usable by non-programmers (accessible UI/UX).
- NF3. Must not block the inference pipeline or degrade frame rate.
- NF4. Must handle missing or corrupted data without crashing.
- NF5. Rendering must be modular—e.g., standalone or embeddable in UI apps.

## Developer(s)
Unassigned

## Priority
Medium (Essential for debugging, not for core inference)

## Example Files
- [sample_landmarks.json](./sample_landmarks.json)
- [annotated_frame_example.png](./annotated_frame_example.png)
- [example_overlay_video.mp4](./example_overlay_video.mp4)

## Open Questions
- Should rendering be WebGL/Plotly-based (JS frontend), OpenCV (Python), or both?
- Should it include confidence scores in the visualizations?
- Do we want side-by-side views (e.g., raw video vs skeleton overlay)?
- Should we support real-time WebSocket streaming for remote visualization?
