# Developer Notes: streamer

## 1. Design Rationale

The `streamer` module is responsible for capturing real-time, multi-modal input from the user and their communication partner. It operates as a session-oriented orchestrator that manages camera and microphone input, extracts structured features (e.g., body landmarks, audio vectors), and stores labeled data for future training or evaluation. It does **not** perform inference directly; instead, it forwards captured data to other modules such as the `gesture_classifier` for real-time classification.

Key architectural decisions:

- **Dual-purpose design**: The streamer supports both training data capture (via labeled recordings) and real-time sessions (where inference may occur). However, inference is delegated to downstream modules. This separation keeps the streamer stateless and reusable.

- **Separation of capture and classification**: Inference models are user-specific and managed by the `gesture_classifier`, allowing the streamer to remain agnostic to model loading, selection, or prediction logic.

- **Concurrent pipelines**: The module runs a recording pipeline (always active) and may stream data to inference modules when appropriate. This enables the system to log new training examples even during live use, supporting continuous learning workflows.

- **Modular stream workers**: Independent workers handle camera and microphone input, allowing for flexibility in source configuration, parallel processing, and future expansion (e.g., multi-camera setups, object detection, or speaker diarization).

- **Session integrity**: All data is tagged with session metadata (session ID, pseudonym, timestamp, modality) to support traceability, auditability, and reproducibility.

Rejected alternatives:
- Combining capture and inference into one module was ruled out to avoid tight coupling, blocking behavior, and reduced testability.
- Capturing raw video/audio without preprocessing (e.g., no landmark/vector extraction in-stream) was rejected due to privacy, storage, and processing constraints.

The design prioritizes flexibility, minimal latency in forwarding, and modularity in how captured data is used.


## 2. Open Questions
List unresolved issues, design uncertainties, or interface decisions still under discussion. These may relate to data formats, control flow, integration, error handling, or performance.

## 3. Known Issues / Risks
Capture any edge cases, potential failure modes, or risks that may require mitigation. This section should be updated as development proceeds.

## 4. Development TODOs
Use this as a checklist of pending implementation steps that are not yet tracked in the issue tracker. Include anything from feature scaffolding to cleanup tasks.

- [ ] Initial implementation
- [ ] Logging integration
- [ ] Schema validation

## 5. Edge Case Handling
Describe any special handling required for non-standard or unexpected input/output conditions. Include assumptions or constraints, even if undecided.

## 6. Integration Notes
Outline how this module is expected to interact with other parts of the system. This may include assumptions about inputs, outputs, timing, or shared data formats.

## 7. References
Add links to relevant specifications, issues, diagrams, research notes, or other documents that inform this module's design or function.
