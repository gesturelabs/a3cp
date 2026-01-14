#for FILE_TREE.txt
tree -a \
  -I '.git|.venv|env|a3cp-env|staticfiles|__pycache__|node_modules|dist|build|*.egg-info|*.pyc|*.pyo|*.pyd|*.log|*.sqlite3|*.db|.DS_Store|.mypy_cache|.ruff_cache|.pytest_cache|.idea|.vscode|.env|.env.*' \
  > docs/FILE_TREE.txt



#activate virtual env
source a3cp-env/bin/activate


#work locally
uvicorn main:app --reload --host 127.0.0.1 --port 8000
http://127.0.0.1:8000/


## Verify POST /schema-recorder/append (Local)

1. Start server: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
2. Open OpenAPI spec directly: http://127.0.0.1:8000/api/openapi.json
3. Search in the JSON for: `/schema-recorder/append`
4. Confirm it appears under `"post"` with the tag `"schema-recorder"`
5. Optional CLI smoke test (will fail with 409 if session dir missing, which is expected):
   `curl -X POST http://127.0.0.1:8000/schema-recorder/append -H "Content-Type: application/json" -d '{}'`
6. If missing: verify `app.include_router(schema_recorder_router)` in `api/main.py`, resta

Done when endpoint appears in /docs.
