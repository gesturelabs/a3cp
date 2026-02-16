# ui/TODO.md — A3CP MVP Demo UI (/a3cp)

Single-page demonstrator for A3CP MVP.

Route: /a3cp
Stack: FastAPI + Jinja + ES module (/static/js/a3cp.js)
No framework. No bundler. No inline JS.
All runtime state owned by A3CPDemoController.
All DOM handled by A3CPDemoUI.
- /a3cp is a hidden demo surface and must not be linked from primary navigation.

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
- seq starts at 01
- Preview always visible
- Preview independent of capture
- Stop Preview stops capture if running
- Manual restart only (no auto-reconnect)
- Silent session validation on load
- Buttons disabled during async operations
-  Explicitly: **No localStorage anywhere in the demo**
-  Only allowed client persistence: `sessionStorage` key `a3cp_demo_session_id`
- UI must never write logs, files, or artifacts; it only calls same-origin HTTP/WS endpoints and renders UI state.
- `record_id` is generated client-side per schema message (one new `record_id` per control/meta message); UI must not reuse `record_id` values.
- Each outbound schema message must include an ISO 8601 UTC `timestamp` generated client-side.
- Preview is independent of capture (users can preview without capturing).



---

# PHASE 1 — PAGE SHELL + CONTROLLER SKELETON

Goal: Static structure + clean architecture.

- [ x] Add /a3cp route in apps/ui/main.py
- [ x] Create templates/a3cp.html
- [ x] Add sections:
  - Session
  - Preview (<video>)
  - Capture
  - Debug (collapsed)
- [x ] Load module:
  <script type="module" src="/static/js/a3cp.js"></script>
- [ x] Create static/js/a3cp.js
- [ x] Implement A3CPDemoUI
- [x] Implement A3CPDemoController
- [x ] Auto-init on DOMContentLoaded


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
- [ ] Disable buttons during async
- [ ] Lock IDs while session active
- On successful End Session:
  - Clear `sessionStorage` key `a3cp_demo_session_id`
  - Reset controller session state to `idle`

Verify:
- [ ] Start → active
- [ ] Refresh → restored
- [ ] End → idle
- [ ] Invalid session auto-clears
- [ ] Buttons disable correctly

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



# PHASE 6 — FRAME LOOP

Goal: Full streaming lifecycle (open → stream → close) with deterministic teardown.

Behavior:
- [ ] Start Capture:
  - [ ] Require active session
  - [ ] Start preview if not already active
  - [ ] Generate new `capture_id` (hidden)
  - [ ] Open WS `/camera_feed_worker/capture`
  - [ ] Send `capture.open` (new `record_id`)
- [ ] Loop frames (bounded interval):
  - [ ] Capture frame to canvas
  - [ ] Encode JPEG
  - [ ] Send `capture.frame_meta` (new `record_id`)
  - [ ] Send binary JPEG bytes (strict ordering)
  - [ ] Increment `seq`
  - [ ] Update Frames Sent
- [ ] Manual Stop:
  - [ ] Send `capture.close` (new `record_id`)
  - [ ] Close WS cleanly
- [ ] Unexpected WS close:
  - [ ] Stop loop immediately
  - [ ] Mark capture stopped
  - [ ] Preview remains active

Verify:
- [ ] `capture.open` accepted
- [ ] Strict meta → binary ordering preserved from first frame
- [ ] No protocol violations
- [ ] No buffer overflow under normal fps
- [ ] No memory growth observed
- [ ] No duplicate `record_id`
- [ ] Clean teardown in all stop paths



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
- Verify UI surfaces these abort/failure cases clearly:
  - protocol violation (`capture.abort` with error_code)
  - limit violation (`capture.abort` with error_code)
  - session invalid/closed (`capture.abort` with error_code or WS close)

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
