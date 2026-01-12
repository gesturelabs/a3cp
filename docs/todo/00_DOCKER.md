## Docker structure (monorepo, contributor workflow)

Scope: MVP dev workflow for isolating heavy-dependency workers.
(Not yet final production deployment.)

- [ ] Add per-module Dockerfiles:
  - [ ] apps/camera_feed_worker/Dockerfile
  - [ ] apps/landmark_extractor/Dockerfile
    - Note: isolate heavy deps (Holistic / OpenCV / MediaPipe)

- [ ] Add repo-root docker-compose.yml (dev):
  - [ ] camera_feed_worker service
  - [ ] landmark_extractor service
  - [ ] No API container yet (runs on host for MVP)

- [ ] Standardize container paths + mounts:
  - [ ] /app   → application code
  - [ ] /data  → artifacts
  - [ ] /logs  → session JSONL logs
  - [ ] Mount host ./data → /data
  - [ ] Mount host ./logs → /logs

- [ ] Standardize shared environment variables:
  - [ ] DATA_ROOT=/data
  - [ ] LOG_ROOT=/logs
  - [ ] APP_ENV (optional)
  - [ ] DEVICE_ID (optional)

- [ ] Document single-command startup:
  - [ ] `docker compose up --build`
