# TODO — A3CP Capture Annotation Integration (Minimal, Blocking-Focused)

## Goal

Fix circular import and correctly model `annotation.intent` as capture-time immutable state in `ActiveState`, without adding non-essential features.

Definition of done:
- Server boots (no circular import)
- Capture WS flow works as before
- `annotation.intent` exists only in `ActiveState`
- Annotation allowed only on `capture.open`

---

## 0. Blocking: Break Circular Import (Do First)

- [ ] Create `apps/camera_feed_worker/state.py`
- [ ] Move from `service.py` to `state.py`:
  - [ ] `PendingMeta`
  - [ ] `IdleState`
  - [ ] `ActiveState`
  - [ ] `State`
- [ ] Add `annotation_intent: str | None = None` to `ActiveState`
- [ ] Update imports:
  - [ ] `service.py` imports state types from `state.py`
  - [ ] `repository.py` imports state types from `state.py`
- [ ] Remove `from ...repository import repo` from `service.py`
- [ ] Confirm server boots

---

## 1. Domain Semantics (Minimal, Correct)

State location (Sprint 1): `ActiveState.annotation_intent`

- [ ] In `handle_open()`:
  - [ ] If `open_event.annotation` exists → set `annotation_intent`
  - [ ] Else → `annotation_intent = None`
- [ ] Do NOT mutate `annotation_intent` anywhere else
- [ ] On `capture.close` → return `IdleState()` (annotation cleared implicitly)
- [ ] On abort → return `IdleState()` (annotation cleared implicitly)

No repo involvement in annotation logic.

---

## 2. Remove Repository Annotation Tracking

- [ ] Remove `"capture_annotation"` from `_ensure()` record
- [ ] Remove:
  - [ ] `get_capture_annotation`
  - [ ] `set_capture_annotation`
  - [ ] `clear_capture_annotation`
- [ ] Ensure no remaining calls to these methods

Repository owns:
- state
- record correlation
- forward buffer
Nothing else.

---

## 3. Schema Constraints

- [ ] Confirm `annotation: Optional[Annotation]` exists on input schema
- [ ] Confirm `Annotation.intent: str` defined
- [ ] Enforce: `annotation` allowed only when `event == "capture.open"`
- [ ] Ensure examples reflect:
  - [ ] `annotation` present only on `capture.open`
  - [ ] Never present in output schema

---

## 4. Router / UI Guardrails

- [ ] Ensure UI sends `annotation.intent` only on `capture.open`
- [ ] Ensure UI never sends `annotation` on:
  - [ ] `capture.frame_meta`
  - [ ] `capture.close`
- [ ] Ensure router contains no annotation-specific repo calls

No additional router features.

---

## 5. Tests (Minimum Required)

### Schema
- [ ] Reject `annotation` when `event != "capture.open"`
- [ ]  Add a test confirming the annotation validator actually triggers based on event, i.e., that event is reliably available at validation time (either via BaseSchema or explicit field).

### Domain
- [ ] `capture.open` sets `ActiveState.annotation_intent`
- [ ] After `capture.close`, state is `IdleState`
- [ ] After abort, state is `IdleState`
- [ ] Annotation isolated per connection_key

Optional (only if trivial):
- [ ] Reject second `capture.open` while active

---

## 6. Explicitly Out of Scope (Later Phase)

- [ ] Persistence of annotation
- [ ] Training integration
- [ ] Label correction linkage
- [ ] Any additional lifecycle features

---

## Completion Criteria

- No circular import
- Service layer contains no repository imports
- Annotation exists only in `ActiveState`
- No new behavioral surface area beyond annotation storage
- All existing capture flows remain stable
