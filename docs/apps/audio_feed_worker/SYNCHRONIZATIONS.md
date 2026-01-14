
# Synchronizations for audio_feed_worker

1. On buffer capture → send waveform to sound_classifier
2. On buffer capture → send waveform to speech_transcriber
3. On buffer capture → send metadata to schema_recorder
4. On device error → notify session_manager
5. On session end → flush and close stream
