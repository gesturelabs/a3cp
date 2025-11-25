# MVP Modules (must be implemented)

- session_manager
- camera_feed_worker
- audio_feed_worker
- landmark_extractor
- gesture_classifier
- sound_classifier
- input_broker
- confidence_evaluator
- clarification_planner
- output_expander (minimal mapping)
- output_planner (minimal)
- partner_ui (minimal demonstrator UI)
- schema_recorder
- recorded_schemas
- model_trainer (basic per-user training)
- model_registry (basic artifact lookup)

# MVP Stubs (must exist but minimal logic)

- speech_transcriber (stub)
- speech_context_classifier (stub)
- visual_environment_classifier (stub)
- llm_clarifier (rule-based stub)
- feedback_log (append-only)
- user_profile_store (static user config)
- retraining_scheduler (manual trigger only)
- sound_playback (optional; simple)

# Post-MVP (not required for Prototype Fund implementation)

- memory_interface
- memory_integrator
- full adaptive memory behavior
- visual_environment_classifier (full implementation)
- speech_context_classifier (real implementation)
- advanced llm_clarifier with semantic reasoning
- advanced output_expander (symbol sets, phrase templates)
- advanced partner_ui (AAC-grade interface)
- automated retraining_scheduler (continuous learning)
- multi-user model management
- environment and context inference modules
- rich landmark_visualizer
