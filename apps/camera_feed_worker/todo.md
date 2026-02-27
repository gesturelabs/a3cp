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

- [x ] Create `apps/camera_feed_worker/state.py`
- [x ] Move from `service.py` to `state.py`:
  - [x ] `PendingMeta`
  - [ x] `IdleState`
  - [ x] `ActiveState`
  - [ x] `State`
- [x ] Add `annotation_intent: str | None = None` to `ActiveState`
- [x ] Update imports:
  - [x ] `service.py` imports state types from `state.py`
  - [ x] `repository.py` imports state types from `state.py`
- [ x] Remove `from ...repository import repo` from `service.py`
- [x ] Confirm server boots

---

## 1. Domain Semantics (Minimal, Correct)

State location (Sprint 1): `ActiveState.annotation_intent`

- [x ] In `handle_open()`:
  - x[ ] If `open_event.annotation` exists → set `annotation_intent`
  - [ x] Else → `annotation_intent = None`
- [x ] Do NOT mutate `annotation_intent` anywhere else
- [x ] On `capture.close` → return `IdleState()` (annotation cleared implicitly)
- [x ] On abort → return `IdleState()` (annotation cleared implicitly)

No repo involvement in annotation logic.

---

## 2. Remove Repository Annotation Tracking

- [x ] Remove `"capture_annotation"` from `_ensure()` record
- [ x] Remove:
  - [ x] `get_capture_annotation`
  - [x ] `set_capture_annotation`
  - [x ] `clear_capture_annotation`
- [ x] Ensure no remaining calls to these methods

Repository owns:
- state
- record correlation
- forward buffer
Nothing else.

---

## 3. Schema Constraints

- [x ] Confirm `annotation: Optional[Annotation]` exists on input schema
- [x ] Confirm `Annotation.intent: str` defined
- [x ] Enforce: `annotation` allowed only when `event == "capture.open"`
- [x ] Ensure examples reflect:
  - [x ] `annotation` present only on `capture.open`
  - [ x] Never present in output schema

---

## 4. Router / UI Guardrails

- [ x] Ensure UI sends `annotation.intent` only on `capture.open`
- [x ] Ensure UI never sends `annotation` on:
  - [ xx] `capture.frame_meta`
  - [x ] `capture.close`
- [x ] Ensure router contains no annotation-specific repo calls

No additional router features.

---

## 5. Tests (Minimum Required)

### Schema
- [x] Reject `annotation` when `event != "capture.open"`
- [ x]  Add a test confirming the annotation validator actually triggers based on event, i.e., that event is reliably available at validation time (either via BaseSchema or explicit field).

### Domain
- [x ] `capture.open` sets `ActiveState.annotation_intent`
- [x ] After `capture.close`, state is `IdleState`
- [ x] After abort, state is `IdleState`
- [x ] Annotation isolated per connection_key

Optional (only if trivial):
- [x ] Reject second `capture.open` while active

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
