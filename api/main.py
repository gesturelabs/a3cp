# api/main.py
from fastapi import FastAPI

from apps.schema_recorder.routes.router import router as schema_recorder_router
from apps.session_manager.routes.router import router as session_manager_router

app = FastAPI(
    title="A3CP API",
    version="1.0.0",
    description="MVP API for session management and module integration",
)

# Mount routers
app.include_router(session_manager_router)
app.include_router(schema_recorder_router)


# Simple root health check
@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
