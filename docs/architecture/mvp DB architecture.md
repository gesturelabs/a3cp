# Minimal DB Architecture for A3CP Demo (Postgres + npz Hybrid)

## Principle
- Store **large Holistic / audio / feature data** as **files** (NPZ) on disk.
- Store **only metadata + pointers + labels + lineage** in Postgres.
- Keep schema stable and small; avoid premature normalization.

---

## Storage Layout (filesystem)
- `data/users/<user_id>/sessions/<session_id>/features/<record_id>.npz`
- `models/users/<user_id>/<modality>/<model_version>/model.bin` (e.g., .pkl/.onnx)
- All file references must be accompanied by `sha256` and encoder/version metadata.

---

## Core Tables (minimum set)

### 1) `users` (optional for demo; can be implicit)
- `user_id` (PK, text)
- `created_at` (timestamptz)

Use if you want FK integrity; otherwise store `user_id` as plain text everywhere.

---

### 2) `training_examples` (demo-critical)
One row = one labeled example pointing to one feature file.
- `example_id` (PK, uuid)
- `user_id` (text, indexed)
- `session_id` (text, nullable, indexed)
- `record_id` (uuid, nullable, unique if present)
- `modality` (text: "gesture"|"audio"|...)
- `label` (text)                      # final/confirmed label
- `label_status` (text)               # "unconfirmed"|"confirmed"|"corrected"
- `performer_id` (text, nullable)
- `timestamp` (timestamptz, indexed)  # when captured/confirmed (pick one, be consistent)
- `features_uri` (text)               # path/URI to npz
- `features_hash` (text)              # "sha256:..."
- `features_format` (text)            # "npz"
- `encoding` (text)                   # e.g. "holistic_landmarks_vX"
- `dims` (int, nullable)
- `consent_given` (bool, default false)
- `is_demo` (bool, default false)
- `created_at` (timestamptz)

Indexes (minimal):
- `(user_id, modality, label)`
- `(user_id, timestamp)`
- unique on `features_hash` OR `(user_id, record_id)` if you need dedupe

---

### 3) `models` (demo-critical “model registry”)
One row = one trained model artifact and its lineage.
- `model_id` (PK, uuid)
- `user_id` (text, indexed)
- `modality` (text: "gesture"|"audio"|...)
- `model_version` (text)              # e.g. "2026-01-06T08:00Z" or semver
- `artifact_uri` (text)               # file path/URI
- `artifact_hash` (text)              # "sha256:..."
- `trainer_name` (text)               # e.g. "baseline_knn" or "lstm_v1"
- `encoding` (text)                   # must match examples encoding used
- `trained_at` (timestamptz, indexed)
- `status` (text)                     # "active"|"candidate"|"archived"
- `notes` (text, nullable)
- `created_at` (timestamptz)

Constraints (minimal):
- at most one active model per `(user_id, modality)` (enforce via partial unique index)

---

### 4) `training_runs` (optional but high leverage)
Captures “what examples produced this model” without complex joins.
- `run_id` (PK, uuid)
- `user_id` (text, indexed)
- `modality` (text)
- `model_id` (uuid)                   # FK to models.model_id (optional)
- `dataset_query` (jsonb)             # snapshot of selection rule, e.g. {label_status:"confirmed", since:"..."}
- `example_count` (int)
- `examples_hash` (text)              # hash of sorted example_ids (dataset fingerprint)
- `started_at` (timestamptz)
- `finished_at` (timestamptz)
- `metrics` (jsonb, nullable)         # simple accuracy/loss if available

This is the minimum to prove “learning happened and is reproducible”.

---

## Sessions (defer DB unless demo requires replay)
For demo, sessions can remain in-memory and only `session_id` is stored in `training_examples`.
If you must persist sessions later, add:
- `sessions(session_id PK, user_id, start_time, end_time, status)`
- `session_events(event_id PK, session_id, event_type, timestamp, payload jsonb)`

---

## Alembic Scope (minimal)
- One initial migration that creates: `training_examples`, `models`, (optional `training_runs`).
- Avoid frequent schema churn by keeping “extra evolving fields” in `jsonb` columns if needed (e.g., `payload jsonb`).

---

## Demo “Persistence Across Restarts” Guarantee
- Training examples persist as: DB row + npz file + hash.
- Active model persists as: DB row (status="active") + artifact file + hash.
- On restart: load latest active model per user/modality from `models`; train uses `training_examples` filtered by `label_status`.
