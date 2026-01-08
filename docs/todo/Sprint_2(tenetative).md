## Sprint 2 — Training Example Capture (Minimal, Explicit)

### Purpose
Make **learning demonstrable** by capturing explicit human feedback tied to existing feature artifacts.

---

### Ground rules
- [ ] **No new raw data** is created here.
- [ ] Every training example **references an existing `record_id`** (feature artifact).
- [ ] One training example = **one row**, append-only.
- [ ] All events recorded via `recorded_schemas` only.

---

### 1) Training example schema (minimal)
- [ ] Define a single TrainingExample schema with fields:
  - `user_id`
  - `session_id`
  - `record_id`
  - `modality` (gesture | sound)
  - `predicted_label`
  - `predicted_confidence`
  - `final_label` (after partner action)
  - `partner_action` (accept | correct)
  - `context_tag?` (optional, short string)
  - `timestamp`
  - `consent_given`
  - `is_demo`

---

### 2) Feedback protocol (strict)
- [ ] System emits a prediction + confidence for an existing `record_id`.
- [ ] Partner must choose exactly one:
  - **Accept** prediction (label stays the same), or
  - **Correct** prediction (select a label).
- [ ] Optional: attach one lightweight context tag.
- [ ] No free-form text.
- [ ] No partial submissions.

---

### 3) Persistence (append-only)
- [ ] Persist each TrainingExample as **one append-only entry**:
  - storage location (one of):
    - `data/users/<user_id>/training/training_examples.jsonl`, or
    - DB table with append-only semantics (implementation choice)
- [ ] Include `record_id` to link back to feature artifact lineage.
- [ ] Emit one A3CPMessage per training example via `recorded_schemas`.

---

### 4) UI (minimal)
- [ ] Extend demo UI to support feedback:
  - display prediction + confidence
  - **Accept** button
  - **Correct** button → label selector
  - optional context tag dropdown
- [ ] Show confirmation that a training example was recorded.
- [ ] Display running count of training examples for the session.

---

### 5) Guardrails
- [ ] Training example **must reference a valid `record_id`** from the same session.
- [ ] Exactly one training example per partner action.
- [ ] No edits or deletes after write.
- [ ] CI test: training example cannot be created without `consent_given`.

---

### Exit gate (Sprint 2 complete)
- [ ] For a session, multiple training examples can be recorded.
- [ ] Each example links cleanly to a `record_id`.
- [ ] Training examples persist across service restarts.
- [ ] Session timeline shows:
  - capture → features → prediction → partner feedback → training example.
