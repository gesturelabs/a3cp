# ui/TODO.md — A3CP MVP Demo UI (surface-scoped, revised order)

This TODO replaces legacy “Demo UI” items from the mono TODO.
It defines **UI-only work** under `ui/`, scoped by user-visible surfaces.
Backend rules, schema validation, persistence, and enforcement live elsewhere.

---

## 0) UI scope & invariants (UI-only)
- UI is same-origin, minimal, and **not linked** from primary navigation
- Runtime state is minimal client-side
- **Session continuity is allowed via `sessionStorage` (tab-scoped) for demo usability**
  - Allowed key:
    - `a3cp_demo_session_id`
  - Constraints:
    - **No `localStorage`**
    - Clear stored session state on `End Session`
- UI never writes logs, files, or artifacts
- UI never re-implements schema rules or backend invariants
- UI responsibilities are limited to:
  - collecting inputs
  - calling demo endpoints
  - rendering success / error states
- Define demo request constants and required input fields (from `BaseSchema`):
  - `schema_version`
  - `user_id`
  - `performer_id`
  - `record_id`
  - `timestamp`
---

## 1) Shared UI utilities (client-only)


### 1.1 SessionContext
- [x ] Implement minimal helper with session-scoped persistence:
  - [x ] `getSessionId(): string | null`
  - [x ] `setSessionId(id: string): void`
  - [ x] `clearSessionId(): void`
- [ x] Add guard helper:
  - [ x] `requireSessionIdOrBlock(actionName)`
- [x] Explicitly:
  - [ x] **Allow `sessionStorage` for `session_id`**
  - [ x] **No `localStorage`**

**Acceptance**
- [ x] Any action requiring a session is blocked in UI if missing
- [ x] Refresh does not clear `session_id`
- [ ] End Session clears stored session state


### 1.2 Shared UI error model
- [x ] Standard error renderer across demo pages:
  - [x ] Action name
  - [ x] HTTP status (if applicable)
  - [x ] Short message
  - [ x] Raw response snippet
- [x ] Network errors clearly distinguished
- [ ] “Clear error” control resets error state only

---

## 2) Surface: `/demo/session` — Session control

### 2.1 Route & page shell
- [ x] Hidden page at `/demo/session`

- [x] SessionContext (sessionStorage-backed)
- [x] Shared error utilities
- [x] /demo/session route exists
- [x] demo_session.html exists (shell)

- [ x] Minimal layout:
  - [x ] Title: “A3CP Demo — Session”
  - [x ] Status indicator: `idle | active | error`
  - [ x] Read-only `session_id` field
  - [ x] Buttons: `Start Session`, `End Session`
  - [ x] Buttons enabled/disabled based on UI state

### 2.2 Start Session action
- [x ] On `Start Session` click:
  - [x ] Call session start endpoint (same-origin)
  - [ x] Include required BaseSchema fields + demo constants
  - [x ] Store returned `session_id` in memory
  - [x ] Update UI state → `active`
- [x ] Error handling:
  - [x ] Render HTTP status + message for non-200
  - [x] Render network errors distinctly
  - [ x] No automatic retries

**Acceptance**
- [ x] Clicking Start shows a non-empty `session_id`


### 2.3 End Session action
- [ x] Enabled only if `session_id` exists in UI
- [ x] On click:
  - [x ] Call session end endpoint with stored `session_id`
  - [ x] Include required BaseSchema fields
  - [xx ] On success: clear state → `idle`
  - [x ] On error: keep state; render error

**Acceptance**
- [ x] End Session impossible without a session
- [x ] Successful end clears UI state

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

### 3.2 Session gating (UI-only)
- [ ] If `session_id` missing:
  - [ ] Disable capture and end-session actions
  - [ ] Show instruction: “Start a session first.”

### 3.3 Session start UX (choose one; keep minimal)
- [ ] Option A: Provide `Start Session` button on `/demo/gesture` reusing `/sessions.start`
- [ ] Option B: No button; show link/instruction to open `/demo/session`

---

### 3.4 Capture window limit
- [ ] Enforce UI-level capture window limit (≤120 seconds):
  - [ ] Show countdown or elapsed time while capturing
  - [ ] Auto-stop capture at 120s if user does not stop manually
  - [ ] Render “auto-stopped at limit” as normal stopped state (not error)

### 3.5 Camera permission & preview
- [ ] On `Start Capture`:
  - [ ] Request camera permission via `getUserMedia()` (video only)
  - [ ] Optional minimal live preview
  - [ ] Permission denied → error, no capture
- [ ] `Stop Capture` stops tracks and updates state

### 3.6 Capture transport (UI responsibility only)
- [ ] Implement capture submission using chosen transport (WebSocket)
- [ ] Connection lifecycle reflected in UI status
- [ ] Send bounded capture window
- [ ] Cleanly finalize on stop
- [ ] `record_id`:
  - [ ] Display backend-provided value
  - [ ] Do **not** generate IDs client-side unless required by contract

### 3.7 Render latest output
- [ ] After capture completes:
  - [ ] Display latest artifact reference/hash if returned
  - [ ] Otherwise show “pending” with manual refresh button
  - [ ] No polling unless later required

**Acceptance**
- [ ] Capture can be started and stopped
- [ ] UI shows capture status and a record identifier or confirmation
- [ ] Capture actions never run without a `session_id`

---

## 4) Explicit non-UI items (out of scope)

These belong to backend modules or tests and are **not** UI TODOs:
- Worker rejection of missing `session_id` (400)
- Backend tests for session enforcement
- Filesystem layout (`DATA_ROOT`, `LOG_ROOT`)
- Artifact integrity, sha256 validation, replay checks
- `(T, D)` correctness and determinism guarantees
- Session JSONL logging rules
