# Submodule: camera_feed_worker

## Purpose

Streaming ingest boundary for bounded video capture windows (Sprint 1: WebSocket).

Validates and forwards JPEG frames incrementally to downstream vision modules.

Does NOT emit `A3CPMessage` and does NOT persist raw frames.

---

## Module Overview

| Field | Value |
|-------|-------|
| Type | worker |
| Inputs | Browser (WebSocket), session_manager |
| Outputs | landmark_extractor |
| Produces A3CPMessage | ❌ No |

---

## Responsibilities

- Accept `capture.open`, `capture.frame_meta`, `capture.close` (JSON)
- Accept `capture.frame_bytes` (binary JPEG)
- Enforce guardrails:
  - Duration
  - FPS
  - Resolution
  - Frame count
  - Byte limits
- Preserve event-time semantics
- Validate and propagate externally authoritative identifiers
- Stream validated frames per-frame (no full-window buffering)
- Emit domain aborts (mapped to WS close by route layer)

---

## Capture Lifecycle (Sprint 1)

Exactly one capture lifecycle per WebSocket:

capture.open
→ frame_meta + frame_bytes*
→ capture.close OR capture.abort


After `capture.close` or `capture.abort`:
- Forwarding stops
- WebSocket closes (1000)
- All per-connection state is cleared

A second `capture.open` on the same connection is prohibited.

---

## Identity Rules

Externally authoritative IDs:
- `record_id`
- `user_id`
- `session_id`
- `capture_id`

Rules:
- Supplied by client only
- Validated and propagated
- Never generated or mutated here

Exception:
- `connection_key` (route-layer only, process-local, never emitted)

During active capture:
- `capture_id` authority resides exclusively in `service.ActiveState`
- Repository maintains no duplicate capture state

---

## Streaming Exception

Per-frame streaming does not use `record_id`.

Correlation uses:

`capture_id + seq`

Frames are transient; the first recorded artifact occurs downstream.

---

## ForwardItem (Internal Forward Envelope)

Self-contained per-frame contract (repository-owned).

Fields:

- `capture_id: str`
- `seq: int`
- `timestamp_frame: datetime`
- `payload: bytes`
- `byte_length: int`
- `encoding: str`
- `width: int`
- `height: int`
- `user_id: str`
- `session_id: str`

### Invariants

- `byte_length == len(payload)`
- No consumer may read `ActiveState`
- No disk writes
- No full-window buffering
- Memory strictly bounded via forward queue limits

---

## Forward Queue Limits (Sprint 1D)

Forward buffer is strictly bounded per capture:

- `max_forward_buffer_frames = 3`
- `max_forward_buffer_bytes = 1_000_000`

On overflow:
- Emit `capture.abort`
- `error_code = "limit_forward_buffer_exceeded"`
- Close WebSocket (1000)

On downstream failure:
- Emit `capture.abort`
- `error_code = "forward_failed"`
- Close WebSocket (1000)

Limits are server-defined and initialized at `capture.open`.

---

## WebSocket Error Policy

| Failure | Abort JSON | Close Code |
|----------|------------|------------|
| JSON parse | No | 1003 |
| Schema error | No | 1008 |
| Idle protocol violation | No | 1008 |
| Active domain abort | Yes | 1000 |
| Internal error | No | 1011 |

---

## Non-Responsibilities

- No inference
- No classification
- No logging
- No schema recording
- No cross-app persistence

---

## Storage Policy

- Raw frames are never persisted
- Only downstream feature artifacts may be recorded

---

## Status

Authoritative for Sprint 1 streaming architecture.
