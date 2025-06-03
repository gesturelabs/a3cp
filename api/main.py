from fastapi import FastAPI
from api.routes.inference import router as inference_router

app = FastAPI(title="A3CP Inference API", version="0.1.0")
app.include_router(inference_router, prefix="/api")
