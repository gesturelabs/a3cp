# api/main.py

from fastapi import FastAPI

# Explicitly import routers from all *_routes.py files
from api.routes.audio_feed_worker_routes import \
    router as audio_feed_worker_router
from api.routes.camera_feed_worker_routes import \
    router as camera_feed_worker_router
from api.routes.clarification_planner_routes import \
    router as clarification_planner_router
from api.routes.confidence_evaluator_routes import \
    router as confidence_evaluator_router
from api.routes.feedback_log_routes import router as feedback_log_router
from api.routes.gesture_classifier_routes import \
    router as gesture_classifier_router
from api.routes.input_broker_routes import router as input_broker_router
from api.routes.landmark_extractor_routes import \
    router as landmark_extractor_router
from api.routes.landmark_visualizer_routes import \
    router as landmark_visualizer_router
from api.routes.llm_clarifier_routes import router as llm_clarifier_router
from api.routes.memory_integrator_routes import \
    router as memory_integrator_router
from api.routes.memory_interface_routes import \
    router as memory_interface_router
from api.routes.model_registry_routes import router as model_registry_router
from api.routes.model_trainer_routes import router as model_trainer_router
from api.routes.output_expander_routes import router as output_expander_router
from api.routes.output_planner_routes import router as output_planner_router
from api.routes.retraining_scheduler_routes import \
    router as retraining_scheduler_router
from api.routes.schema_recorder_routes import router as schema_recorder_router
from api.routes.session_manager_routes import router as session_manager_router
from api.routes.sound_classifier_routes import \
    router as sound_classifier_router
from api.routes.sound_playback_routes import router as sound_playback_router
from api.routes.speech_context_classifier_routes import \
    router as speech_context_classifier_router
from api.routes.speech_transcriber_routes import \
    router as speech_transcriber_router
from api.routes.visual_environment_classifier_routes import \
    router as visual_environment_classifier_router
from api.settings import get_settings

settings = get_settings()
app = FastAPI(title="A3CP Inference API", version="0.5.x")

# Include all routers under the same prefix for now
app.include_router(audio_feed_worker_router, prefix="/api/audio_feed_worker")
app.include_router(camera_feed_worker_router, prefix="/api/camera_feed_worker")
app.include_router(clarification_planner_router, prefix="/api/clarification_planner")
app.include_router(confidence_evaluator_router, prefix="/api/confidence_evaluator")
app.include_router(feedback_log_router, prefix="/api/feedback_log")
app.include_router(gesture_classifier_router, prefix="/api/gesture_classifier")
app.include_router(input_broker_router, prefix="/api/input_broker")
app.include_router(landmark_extractor_router, prefix="/api/landmark_extractor")
app.include_router(landmark_visualizer_router, prefix="/api/landmark_visualizer")
app.include_router(llm_clarifier_router, prefix="/api/llm_clarifier")
app.include_router(memory_integrator_router, prefix="/api/memory_integrator")
app.include_router(memory_interface_router, prefix="/api/memory_interface")
app.include_router(model_registry_router, prefix="/api/model_registry")
app.include_router(model_trainer_router, prefix="/api/model_trainer")
app.include_router(output_expander_router, prefix="/api/output_expander")
app.include_router(output_planner_router, prefix="/api/output_planner")
app.include_router(retraining_scheduler_router, prefix="/api/retraining_scheduler")
app.include_router(schema_recorder_router, prefix="/api/schema_recorder")
app.include_router(session_manager_router, prefix="/api/session_manager")
app.include_router(sound_classifier_router, prefix="/api/sound_classifier")
app.include_router(sound_playback_router, prefix="/api/sound_playback")
app.include_router(
    speech_context_classifier_router, prefix="/api/speech_context_classifier"
)
app.include_router(speech_transcriber_router, prefix="/api/speech_transcriber")
app.include_router(
    visual_environment_classifier_router, prefix="/api/visual_environment_classifier"
)


if __name__ == "__main__":
    import uvicorn

    print(
        f"🔧 Starting FastAPI (DEV) | ENV={settings.ENVIRONMENT} | DB={settings.DB_NAME}"
    )
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.UVICORN_PORT, reload=True)
