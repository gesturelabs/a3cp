# Submodule: camera_feed_worker

## Purpose

Streaming ingest boundary for bounded video capture windows (Sprint 1: browser via WebSocket).

Validates and forwards JPEG frames incrementally to downstream vision modules.

Does NOT emit A3CPMessage and does NOT persist raw frames.

---

## Module Overview

| Field | Value |
|-------|-------|
| Type | worker |
| Inputs | Browser (WebSocket), session_manager (session validation) |
| Outputs | landmark_extractor (and other vision modules) |
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
- Preserve event-time (`timestamp_start`, `timestamp_frame`, `timestamp_end`)
- Validate and propagate:
  - `user_id`
  - `session_id`
  - `capture_id`
- Stream validated frames incrementally (no full-window buffering)
- Emit domain aborts (mapped to WS close by route layer)

---

## Identity Rules

Control-plane messages reuse:

- `schema_version`
- `record_id`
- `user_id`
- `session_id`

`record_id`:
- Identifies a control message only
- Unique per WebSocket connection
- Not persisted
- Not generated here

### Streaming Exception

For raw frame streaming:

- No per-frame `record_id`
- Correlation uses `capture_id + seq`
- Frames are transient and not recorded
- First recorded artifact occurs downstream

This module never generates identifiers owned by other modules.

---

## Forwarded Frame (Internal, In-Memory)

ForwardedFrame {
capture_id
user_id
session_id
seq
timestamp_frame
encoding
byte_length
bytes (memory only)
}


- Forwarded immediately after validation
- No disk writes
- Memory strictly bounded

Optional `CaptureSummary` on close.

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

## Storage Policy (Sprint 1)

- Raw frames never persisted
- Only downstream feature artifacts may be recorded
- Logging authority: `recorded_schemas` only

---

## Status

Authoritative for Sprint 1 streaming architecture.
