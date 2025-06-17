#api/main.py
from fastapi import FastAPI
from api.settings import get_settings
from api.routes.inference import router as inference_router
from api.routes.streamer import router as streamer_router
from api.routes import gesture_infer
from api.routes import sound_infer


settings = get_settings()
app = FastAPI(title="A3CP Inference API", version="0.1.0")

app.include_router(inference_router, prefix="/api/infer")
app.include_router(streamer_router, prefix="/api/streamer")
app.include_router(gesture_infer.router, prefix="/api/gesture")
app.include_router(sound_infer.router, prefix="/api/sound")


if __name__ == "__main__":
    import uvicorn
    print(f"🔧 Starting FastAPI (DEV) | ENV={settings.ENVIRONMENT} | DB={settings.DB_NAME}")
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.UVICORN_PORT, reload=True)
