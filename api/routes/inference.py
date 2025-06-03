from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/infer/")
async def infer_stub():
    return JSONResponse({
        "message_type": "A3CPMessage",
        "status": "ok",
        "detail": "FastAPI inference stub is alive."
    })
