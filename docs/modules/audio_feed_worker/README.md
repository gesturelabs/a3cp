# Submodule: audio_feed_worker

## Purpose
Captures live audio from a local input device (e.g., microphone) and streams it to downstream modules in real time.
Acts as the source for all audio-derived data such as waveform-based classification, transcription, and recording.

## Responsibilities
- Open and manage access to the selected audio input device
- Stream raw audio buffers with consistent sample rate and chunk size
- Timestamp each buffer accurately for synchronization
- Forward audio chunks to downstream consumers (e.g., SoundClassifier, SpeechTranscriber)
- Signal availability/failure of audio input to orchestrating modules

## Not Responsible For
- Audio classification or transcription
- Waveform visualization or playback
- File I/O or schema-compliant recording
- Inference logic or context interpretation
- Session orchestration or storage

## Inputs
- Configuration parameters:
  - `device_index` (e.g., default mic, external mic index)
  - `sample_rate` (e.g., 16000, 44100)
  - `chunk_size` (e.g., 1024 samples per frame)
- Optional metadata (forwarded if available):
  - `session_id`, `user_id`, `pseudonym`

## Outputs
- Timestamped audio chunks (e.g., `np.ndarray` or `bytes`)
- Stream metadata (e.g., `chunk_id`, `timestamp`, `device_index`)
- Error signals (e.g., mic unavailable, buffer overrun)

## Runtime Considerations
- Must support threaded or asynchronous capture to avoid blocking audio I/O
- Exposes interface (e.g., generator, callback, queue) for downstream use
- Audio input failures must emit recoverable exceptions and diagnostics
- Graceful shutdown and reinitialization between sessions
- Optional silence detection or amplitude thresholding

---

## Design Rationale
The `AudioFeedWorker` was separated from the original video/audio streamer to ensure single-responsibility modularity.
This submodule specializes in continuous real-time waveform capture for multimodal classification and transcription.

### Architectural Decisions:
- No side effects: no file writing, classification, or transformation
- Deterministic timestamps: used for temporal alignment across modalities
- Device-agnostic: supports internal mics, USB mics, and virtual devices
- Resilience-first: handles permission errors, silence, dropouts gracefully

---

## Edge Case Handling
- Logs and fails gracefully if no audio device is detected
- Recovers from buffer underruns or overflow
- Timestamps must be monotonic even during silence or buffer skips
- Optional dev mode for waveform injection from `.wav` files
- Logs duration of silence or abnormal amplitude (if enabled)

---

## Known Issues / Risks
- Mic permission handling may block on some platforms (macOS, Android)
- Sample rate mismatches can cause distortion if resampling is not handled
- Threaded audio capture can interfere with some UI environments
- Channel count (mono/stereo) must be validated and normalized
- Hot-plugged audio devices may break stream mid-session

---

## Development TODOs
- [ ] Implement threaded capture using `sounddevice` or `pyaudio`
- [ ] Expose queue or generator for streaming output
- [ ] Add silence detection and amplitude statistics
- [ ] Implement `dev_mode` fallback using `.wav` file
- [ ] Log mic detection, stream start/stop, buffer issues
- [ ] Validate input/output schema compatibility with `RawActionRecord`

---

## Open Questions
- Should we support stereo input or always downmix to mono?
- Should silence thresholds trigger internal logging or external callbacks?
- Should we offer in-module resampling if device rate differs from target?
- Do we expose amplitude features (RMS, peak) or leave to downstream?

---

## Integration Notes
- **To SoundClassifier**: Streams chunks via buffer/pipe
- **To SpeechTranscriber**: Streams waveform with timing metadata
- **To SchemaRecorder**: Metadata attached downstream
- **From Config Manager**: Pulls device index, rate, chunk size
- **Output schema**: Raw waveform with frame-level timestamping

---

## References
- [`SCHEMA_REFERENCE.md`](../../schemas/SCHEMA_REFERENCE.md) — audio input field definitions
- [`sound_classifier/README.md`](../sound_classifier/README.md) — consumer expectations
- [`audio_feed_architecture.drawio`](./diagrams/audio_feed_architecture.drawio) — architecture diagram (WIP)
- A3CP Design Doc v3 – Section 6.3 (Audio Stream Stack)
- SoundDevice: https://python-sounddevice.readthedocs.io/
- PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
