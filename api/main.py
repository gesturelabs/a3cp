# api/main.py
from fastapi import FastAPI

from api.routes.session_manager_routes import router as session_manager_router

app = FastAPI(
    title="A3CP API",
    version="1.0.0",
    description="MVP API for session management and module integration",
)

# Only mount session_manager for now
app.include_router(session_manager_router)


# Simple root health check
@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
