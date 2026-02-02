# ui/TODO.md — A3CP MVP Demo UI (surface-scoped)

This TODO replaces legacy “Demo UI” items from the mono TODO.
It defines **UI-only work** under `ui/`, scoped by user-visible surfaces.
Backend rules, schema validation, persistence, and enforcement live elsewhere.

---

## 0) UI scope & invariants (UI-only)
- [ ] UI is same-origin, minimal, and **not linked** from primary navigation
- [ ] Runtime state is client-side and minimal
- [ ] **Session continuity is allowed via `sessionStorage` for demo usability**
  - [ ] Allowed keys (demo-only):
    - [ ] `a3cp_demo_session_id`
    - [ ] `a3cp_demo_record_id` (optional; only if needed)
  - [ ] Constraints:
    - [ ] **No `localStorage`**
    - [ ] Clear these keys on `End Session`
    - [ ] Provide a `Reset Demo` control that clears these keys + UI state
- [ ] UI never writes logs, files, or artifacts
- [ ] UI never re-implements schema rules or backend invariants
- [ ] UI responsibilities are limited to:
  - collecting inputs
  - calling demo endpoints
  - rendering success / error states

---

## 1) Surface: `/demo/session` — Session control

### 1.1 Route & page shell
- [ ] Hidden page at `/demo/session`
- [ ] Minimal layout:
  - [ ] Title: “A3CP Demo — Session”
  - [ ] Status indicator: `idle | active | error`
  - [ ] Read-only `session_id` field
  - [ ] Buttons: `Start Session`, `End Session`, `Reset Demo`
  - [ ] Buttons enabled/disabled based on UI state

### 1.2 Start Session action
- [ ] On `Start Session` click:
  - [ ] Call session start endpoint (same-origin)
  - [ ] Store returned `session_id` in `sessionStorage` (`a3cp_demo_session_id`)
  - [ ] Update UI state → `active`
- [ ] Error handling:
  - [ ] Render HTTP status + message for non-200
  - [ ] Render network errors distinctly
  - [ ] No automatic retries

**Acceptance**
- [ ] Clicking Start shows a non-empty `session_id`
- [ ] Refresh does not lose `session_id`
- [ ] `Reset Demo` clears `session_id` and UI state

### 1.3 End Session action
- [ ] Enabled only if `session_id` exists in UI
- [ ] On click:
  - [ ] Call session end endpoint with stored `session_id`
  - [ ] On success: clear `sessionStorage` keys → `idle`
  - [ ] On error: keep state; render error

**Acceptance**
- [ ] End Session impossible without a session
- [ ] Successful end clears `session_id` and UI state

---

## 2) Shared UI utility: SessionContext (client-only)

- [ ] Implement minimal helper (session-scoped persistence):
  - [ ] `getSessionId(): string | null` (reads `sessionStorage`)
  - [ ] `setSessionId(id: string): void` (writes `sessionStorage`)
  - [ ] `clearSessionId(): void` (removes key)
- [ ] Add guard helper:
  - [ ] `requireSessionIdOrBlock(actionName)`
- [ ] Explicitly:
  - [ ] **Allow `sessionStorage` only**
  - [ ] **No `localStorage`**

**Acceptance**
- [ ] Any action requiring a session is blocked in UI if missing
- [ ] Refresh does not clear `session_id`
- [ ] End Session / Reset Demo clears `session_id`

---

## 3) Surface: `/demo/gesture` — Gesture capture (MVP)

### 3.1 Page shell & controls
- [ ] Hidden page at `/demo/gesture`
- [ ] Display (read-only):
  - [ ] `session_id`
  - [ ] `record_id` (blank until capture)
  - [ ] Capture status: `idle | capturing | stopped | error`
  - [ ] Latest artifact ref/hash (if available)
- [ ] Buttons:
  - [ ] `Start Capture`
  - [ ] `Stop Capture`
  - [ ] `End Session`
  - [ ] `Reset Demo`

### 3.2 Session gating (UI-only)
- [ ] If `session_id` missing:
  - [ ] Disable capture and end-session actions
  - [ ] Show instruction: “Start a session first.”

### 3.3 Camera permission & preview
- [ ] On `Start Capture`:
  - [ ] Request camera permission via `getUserMedia()` (video only)
  - [ ] Optional minimal live preview
  - [ ] Permission denied → error, no capture
- [ ] `Stop Capture` stops tracks and updates state

### 3.4 Capture transport (UI responsibility only)
- [ ] Implement capture submission using chosen transport (WebSocket)
- [ ] Connection lifecycle reflected in UI status
- [ ] Send bounded capture window
- [ ] Cleanly finalize on stop
- [ ] `record_id`:
  - [ ] Display backend-provided value
  - [ ] Store in `sessionStorage` only if needed (`a3cp_demo_record_id`)
  - [ ] Do **not** generate IDs client-side unless required by contract

### 3.5 Render latest output
- [ ] After capture completes:
  - [ ] Display latest artifact reference/hash if returned
  - [ ] Otherwise show “pending” with manual refresh button
  - [ ] No polling unless later required

**Acceptance**
- [ ] Capture can be started and stopped
- [ ] UI shows capture status and a record identifier or confirmation
- [ ] Capture actions never run without a `session_id`

### 3.x Capture window limit + optional session shortcut
- [ ] Enforce a UI-level capture window limit (≤120 seconds):
  - [ ] Show countdown or elapsed time while capturing
  - [ ] Auto-stop capture at 120s if user does not stop manually
  - [ ] Render “auto-stopped at limit” as a normal stopped state (not an error)

- [ ] Session start UX (choose one; keep minimal):
  - [ ] Option A: Provide `Start Session` button on `/demo/gesture` that reuses the same start call as `/demo/session`
  - [ ] Option B: No button; show link/instruction to open `/demo/session` and start there

---

## 4) Shared UI error model
- [ ] Standard error renderer across demo pages:
  - [ ] Action name
  - [ ] HTTP status (if applicable)
  - [ ] Short message
  - [ ] Raw response snippet
- [ ] Network errors clearly distinguished
- [ ] “Clear error” control resets error state only

---

## 5) Explicit non-UI items (out of scope here)

These belong to backend modules or tests and are **not** UI TODOs:
- Worker rejection of missing `session_id` (400)
- Backend tests for session enforcement
- Filesystem layout (`DATA_ROOT`, `LOG_ROOT`)
- Artifact integrity, sha256 validation, replay checks
- `(T, D)` correctness and determinism guarantees
- Session JSONL logging rules

---
