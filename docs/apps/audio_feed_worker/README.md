# Submodule: audio_feed_worker



## Purpose
Captures live audio from a local input device (e.g., microphone) and streams it to downstream modules in real time.
Acts as the source for all audio-derived data such as waveform-based classification, transcription, and logging.

| Field             | Value                  |
|------------------|------------------------|
| **Module Name**  | `audio_feed_worker`    |
| **Module Type**  | `worker`               |
| **Inputs From**  | `session_manager`       |
| **Outputs To**   | `sound_classifier`, `speech_transcriber`, `schema_recorder` |
| **Produces A3CPMessage?** | ❌ No (metadata only, schema wrapping downstream) |


## Responsibilities
- Open and manage access to the selected audio input device
- Stream raw audio buffers with consistent sample rate and internal buffer size (`chunk_size`)
- Timestamp each buffer accurately for synchronization
- Forward audio chunks to downstream consumers (e.g., SoundClassifier, SpeechTranscriber)
- Signal availability/failure of audio input to orchestrating modules

## Not Responsible For
- Audio classification or transcription
- Waveform visualization or playback
- File I/O or schema-compliant recording
- Inference logic or context interpretation
- Session orchestration or final logging

## Inputs
Configuration parameters (provided at runtime via `session_manager`):

- `device_index`    – Integer index of selected audio device (e.g., 0, 1, 2)
- `sample_rate`     – Audio sample rate in Hz (e.g., 16000, 44100)
- `chunk_size`      – Buffer size in samples per frame (e.g., 1024)

> Note: `chunk_size` is an **internal buffer parameter** used for stream I/O.
> It is not part of any logged schema. Synchronization is handled downstream
> using `timestamp` and `session_id`.

Optional metadata (forwarded if available):

- `session_id`      – Unique session identifier
- `user_id`         – Pseudonymous user identifier
- `device_id`       – Logical source identifier for the capture hardware

## CONFIGURATION SOURCE

`audio_feed_worker` does **not** manage its own configuration.

All runtime parameters are passed to it by the `session_manager`, which may
aggregate them from user profiles, static configs, or UI selections.

This design ensures:

- Configuration is decoupled from signal capture logic
- The module is device-agnostic and reentrant
- No persistent state or file I/O is required within the module

## Outputs
- Timestamped audio chunks (e.g., `np.ndarray` or `bytes`)
- Metadata attached per chunk (e.g., `timestamp`, `device_index`)
- Error signals (e.g., mic unavailable, buffer overrun)

⚠ SCHEMA COMPLIANCE DISCLAIMER
This module does **not** emit `A3CPMessage` records.

Instead, it streams raw audio data with lightweight metadata to downstream
consumers (e.g., `sound_classifier`, `speech_transcriber`, `schema_recorder`).

It is the responsibility of those downstream modules to:

- Wrap each audio frame into a schema-compliant `A3CPMessage`
- Ensure inclusion of required fields (`timestamp`, `session_id`, `modality`, etc.)
- Validate compatibility with the canonical runtime schema (`SCHEMA_REFERENCE.md`)

This design preserves modularity and ensures that schema constraints do not
interfere with low-latency signal acquisition.

### Output Payload Format (internal)

While `audio_feed_worker` does not emit a schema-compliant `A3CPMessage`, it produces a structured data payload that is consumed by downstream modules. Each emitted frame includes:


{
  "audio_data": <bytes or np.ndarray>,     # Raw waveform buffer
  "timestamp": <ISO 8601 string>,          # UTC time of frame capture
  "sample_rate": <int>,                    # Sample rate in Hz
  "device_index": <int>,                   # Audio device identifier
  "session_id": <str, optional>,           # Pseudonymous session ID
  "user_id": <str, optional>,              # Pseudonymous user ID
  "device_id": <str, optional>             # Logical input source ID
}

This payload must be:
-Passed via in-memory queue, callback, or stream pipe
-Wrapped by downstream consumers (e.g., schema_recorder, speech_transcriber) into schema-compliant logs
-Timestamped with millisecond precision and aligned with session context

## Runtime Considerations
- Must support threaded or asynchronous capture to avoid blocking audio I/O
- Exposes interface (e.g., generator, callback, or queue) for downstream use
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
- [ ] Validate compatibility with downstream `A3CPMessage` schema

---

## Open Questions
- Should we support stereo input or always downmix to mono?
- Should silence thresholds trigger internal logging or external callbacks?
- Should we offer in-module resampling if device rate differs from target?
- Do we expose amplitude features (RMS, peak) or leave to downstream?

---

## Integration Notes
- **To SoundClassifier**: Streams audio chunks via buffer/pipe
- **To SpeechTranscriber**: Streams waveform with timestamp metadata
- **To SchemaRecorder**: Metadata attached downstream for schema compliance
- **From Session Manager**: Pulls device index, sample rate, chunk size
- **Output format**: Raw waveform array + metadata; schema wrapping done downstream

---

## References
- [`SCHEMA_REFERENCE.md`](../../schemas/SCHEMA_REFERENCE.md) — defines `modality`, `source`, `device_id`, `timestamp`, and logging expectations
- [`sound_classifier/README.md`](../sound_classifier/README.md) — consumer expectations
- [`audio_feed_architecture.drawio`](./diagrams/audio_feed_architecture.drawio) — architecture diagram (WIP)
- A3CP Design Doc v3 – Section 6.3 (Audio Stream Stack)
- [SoundDevice](https://python-sounddevice.readthedocs.io/)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
