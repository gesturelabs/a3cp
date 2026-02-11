# ui/TODO.md — A3CP MVP Demo UI (/a3cp)

Single-page demonstrator for A3CP MVP.

Route: /a3cp
Stack: FastAPI + Jinja + ES module (/static/js/a3cp.js)
No framework. No bundler. No inline JS.
All runtime state owned by A3CPDemoController.
All DOM handled by A3CPDemoUI.

---

## GLOBAL INVARIANTS (LOCKED)

- Single page only (/a3cp)
- No navigation-based state
- ES module (type="module")
- No global exports
- schema_version = "1.0.1" (hardcoded)
- WebSocket path = /camera_feed_worker/capture
- user_id, performer_id, session_id visible
- record_id visible (read-only)
- capture_id hidden
- seq starts at 0 (UI shows Frames Sent = seq + 1)
- Preview always visible
- Preview independent of capture
- Stop Preview stops capture if running
- Manual restart only (no auto-reconnect)
- Silent session validation on load
- Buttons disabled during async operations
-  Explicitly: **No localStorage anywhere in the demo**
-  Only allowed client persistence: `sessionStorage` key `a3cp_demo_session_id`


---

# PHASE 1 — PAGE SHELL + CONTROLLER SKELETON

Goal: Static structure + clean architecture.

- [ ] Add /a3cp route in apps/ui/main.py
- [ ] Create templates/a3cp.html
- [ ] Add sections:
  - Session
  - Preview (<video>)
  - Capture
  - Debug (collapsed)
- [ ] Load module:
  <script type="module" src="/static/js/a3cp.js"></script>
- [ ] Create static/js/a3cp.js
- [ ] Implement A3CPDemoUI
- [ ] Implement A3CPDemoController
- [ ] Auto-init on DOMContentLoaded
- [ ] No runtime logic yet

Verify:
- [ ] Page loads without console errors
- [ ] Controller initializes once
- [ ] No globals leaked

---

# PHASE 2 — SESSION LIFECYCLE (HTTP ONLY)

Goal: Fully working session independent of camera.

UI:
- [ ] Editable user_id
- [ ] Editable performer_id (defaults to user_id while idle)
- [ ] Read-only session_id
- [ ] Buttons: Start Session / End Session

Behavior:
- [ ] Restore session_id from sessionStorage on load
- [ ] Validate silently via backend
- [ ] If invalid → clear storage
- [ ] Disable buttons during async
- [ ] Lock IDs while session active

Verify:
- [ ] Start → active
- [ ] Refresh → restored
- [ ] End → idle
- [ ] Invalid session auto-clears
- [ ] Buttons disable correctly

### UI (add button)
- [ ] Add `Reset Demo` button

### Behavior
- [ ] Reset Demo:
  - Clears `sessionStorage` (`a3cp_demo_session_id`)
  - Resets controller state to `idle`
  - Unlocks `user_id` and `performer_id`
  - Disabled while capturing

### Verify
- [ ] Reset clears session and UI state
- [ ] Preview remains unaffected
- [ ] Capture must not be active when Reset is clickable
---

# PHASE 3 — PREVIEW ONLY (NO WEBSOCKET)

Goal: Isolate media lifecycle.

UI:
- [ ] Start Preview
- [ ] Stop Preview
- [ ] Always-visible preview window

Behavior:
- [ ] Start Preview → getUserMedia(video)
- [ ] Attach stream to <video>
- [ ] Stop Preview → stop tracks
- [ ] If capturing → Stop Preview triggers capture teardown

Verify:
- [ ] Permission works
- [ ] No duplicate streams
- [ ] Tracks stop cleanly

---

# PHASE 4 — WEBSOCKET CONTROL PLANE (NO FRAMES)

Goal: Verify capture.open / capture.close only.

UI:
- [ ] Start Capture
- [ ] Stop Capture
- [ ] WS Status label
- [ ] Capturing indicator (● Capturing)
- [ ] record_id visible (read-only)
- [ ] Frames Sent visible

Behavior:
- [ ] Start Capture requires session active
- [ ] If preview inactive → start preview
- [ ] Generate capture_id (one per capture, hidden)
- [ ] Generate new record_id per control message
- [ ] Open WS /camera_feed_worker/capture
- [ ] Send capture.open
- [ ] Stop Capture sends capture.close
- [ ] Unexpected WS close:
  - Stop capture
  - WS status = closed
  - Preview remains active

Verify:
- [ ] WS connects
- [ ] open accepted
- [ ] close clean
- [ ] No state leakage
- [ ] record_id unique per message

---

# PHASE 5 — SINGLE FRAME SEND

Goal: Verify strict meta + binary ordering.

Behavior:
- [ ] Canvas capture
- [ ] Encode JPEG
- [ ] Send capture.frame_meta (new record_id)
- [ ] Send binary JPEG bytes
- [ ] seq = 0
- [ ] Frames Sent = 1

Verify:
- [ ] No abort
- [ ] Byte length correct
- [ ] WS stable

---

# PHASE 6 — FRAME LOOP

Goal: Real streaming behavior.

Behavior:
- [ ] Loop frames (bounded interval)
- [ ] Increment seq
- [ ] Update Frames Sent
- [ ] Manual Stop works

Verify:
- [ ] No buffer overflow under normal fps
- [ ] No memory growth observed
- [ ] No duplicate record_id
- [ ] Clean teardown

---

# PHASE 7 — ABORT & EDGE CASES

Goal: Deterministic teardown.

Scenarios:
- [ ] Stop Preview during capture
- [ ] Session closed mid-capture
- [ ] Network disconnect
- [ ] Forward failure (if inducible)

Verify:
- [ ] Capture stops immediately
- [ ] WS closed
- [ ] Preview remains active
- [ ] No ghost state

---
## GLOBAL UI STRUCTURE — ADD ERROR BLOCK

(Add after all main sections, at bottom of page)

### Error Panel (Collapsed by Default)
- [ ] Add bottom-of-page error block
- [ ] Shows only most recent error
- [ ] Displays:
  - Short error message
  - HTTP status (if applicable)
  - `error_code` (if from `capture.abort`)
- [ ] Add `Clear Error` button
- [ ] Panel hidden when no error

### Verify
- [ ] Errors from session start/end display correctly
- [ ] `capture.abort` error_code visible
- [ ] Clear Error hides panel
- [ ] No error stacking

# camera_feed_worker VERIFIED WHEN

- Full lifecycle works from /a3cp
- No protocol violations
- No record_id duplication
- No state leakage
- Deterministic teardown in all paths
- Forward limits respected
- Manual restart behaves predictably
