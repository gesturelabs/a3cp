# ✅ A3CP Canonical Schema → Route → Test Workflow

This workflow defines the full integration path from stable Pydantic schemas to FastAPI routes and Pytest-based validation.

---

## 🧱 Step 0: Project Setup (one time)

- All schemas live in: schemas/<module>/<module>.py
- All routes live in: api/routes/<module>_routes.py
- All tests live in: tests/api/test_<module>_routes.py
- Each schema should define:
  - Input and output models
  - (Optional) example_input() and example_output() for test scaffolding

---

## 🔁 Per-Module Workflow

### 1. You provide the schema
- Paste the contents of schemas/<module>/<module>.py
- Optionally specify:
  - Input/output model names
  - Desired route path
  - Expected behavior

---

### 2. Assistant generates the route
- File: api/routes/<module>_routes.py
- Contains:
  - APIRouter instance
  - One or more endpoint functions
  - Type-annotated input/output models
  - Return value from example_output() (if defined)

---

### 3. You paste the route into your codebase

bash
# Example:
vim api/routes/audio_feed_worker_routes.py
# or open in VS Code



---

### 4. Assistant generates the test
- File: tests/api/test_<module>_routes.py
- Sends POST with example_input()
- Asserts:
  - status_code == 200
  - Key response fields

---

### 5. You run the test

bash
pytest tests/api/test_<module>_routes.py



- Confirm it passes
- Debug if needed

---
### 6. Repeat for next module
log in changelog.md

### 7. Repeat for next module

---

## 🧹 Post-Stability Tasks

- Expand tests to include validation, error paths, edge cases
- Group routes by purpose (e.g. /api/infer, /api/log)
- Add OpenAPI metadata (tags, summary)
- CI enforcement: schema sync, route coverage
- Auto-generate client SDKs (optional)
