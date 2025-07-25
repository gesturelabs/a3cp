{
    "module_name": "audio_feed_worker",
    "module_type": "worker",
    "inputs_from": [
        "config_manager"
    ],
    "outputs_to": [
        "sound_classifier",
        "speech_transcriber",
        "schema_recorder"
    ]
}

{
    "module_name": "camera_feed_worker",
    "module_type": "worker",
    "inputs_from": [
        "session_manager"
    ],
    "outputs_to": [
        "landmark_extractor",
        "visual_environment_classifier"
    ]
}

{
    "module_name": "clarification_planner",
    "module_type": "coordinator",
    "inputs_from": [
        "confidence_evaluator",
    ],
    "outputs_to": [
        "llm_clarifier",
        "output_expander"
    ]
}

{
    "module_name": "confidence_evaluator",
    "module_type": "coordinator",
    "inputs_from": [
        "input_broker",
        "memory_integrator"
    ],
    "outputs_to": [
        "clarification_planner"
    ]
}


{
  "module_name": "feedback_log",
  "module_type": "memory",
  "inputs_from": [
    "clarification_planner",
    "llm_clarifier"
  ],
  "outputs_to": [
    "memory_interface"
  ]
}



{
    "module_name": "gesture_classifier",
    "module_type": "classifier",
    "inputs_from": [
        "landmark_extractor",
        "model_registry"
    ],
    "outputs_to": [
        "input_broker"
    ]
}

{
  "module_name": "input_broker",
  "module_type": "coordinator",
  "inputs_from": [
    "gesture_classifier",
    "sound_classifier",
    "speech_context_classifier",
    "visual_environment_classifier"
  ],
  "outputs_to": [
    "confidence_evaluator",
    "schema_recorder"
  ]
}

{
    "module_name": "landmark_extractor",
    "module_type": "classifier",
    "inputs_from": [
        "camera_feed_worker"
    ],
    "outputs_to": [
        "gesture_classifier",
        "schema_recorder"
    ]
}

{
    "module_name": "landmark_visualizer",
    "module_type": "visualizer",
    "inputs_from": [
        "recorded_schemas"
    ],
    "outputs_to": [
      "partner_ui"
    ]
}

{
    "module_name": "llm_clarifier",
    "module_type": "classifier",
    "inputs_from": [
        "clarification_planner",
        "user_profile_store"
    ],
    "outputs_to": [
        "output_expander",
        "feedback_log",
        "partner_ui"
    ]
}

{
    "module_name": "memory_integrator",
    "module_type": "coordinator",
    "inputs_from": [
        "memory_interface"
    ],
    "outputs_to": [
        "confidence_evaluator"
    ]
}

{
    "module_name": "memory_interface",
    "module_type": "memory",
    "inputs_from": [
        "clarification_planner",
        "feedback_log"
    ],
    "outputs_to": [
        "memory_integrator"
    ]
}

{
    "module_name": "model_registry",
    "module_type": "memory",
    "inputs_from": [
        "model_trainer"
    ],
    "outputs_to": [
        "gesture_classifier",
        "sound_classifier",
        "speech_context_classifier",
        "visual_environment_classifier"
    ]
}
{
    "module_name": "model_trainer",
    "module_type": "model",
    "inputs_from": [
        "recorded_schemas",
        "user_profile_store",
        "retraining_scheduler"
    ],
    "outputs_to": [
        "model_registry"
    ]
}


{
    "module_name": "output_expander",
    "module_type": "coordinator",
    "inputs_from": [
        "clarification_planner",
        "llm_clarifier",
        "user_profile_store"
    ],
    "outputs_to": [
        "output_planner"
    ]
}

{
    "module_name": "output_planner",
    "module_type": "coordinator",
    "inputs_from": [
        "output_expander",
        "user_profile_store"
    ],
    "outputs_to": [
        "partner_ui"
    ]
}

{
    "module_name": "partner_ui",
    "module_type": "interface",
    "inputs_from": [
        "output_planner",
        "landmark_visualizer",
        "sound_playback",
        "llm_clarifier"
    ],
    "outputs_to": [
        "session_manager",
        "retraining_scheduler",
        "feedback_log",
        "user_profile_store",
        "llm_clarifier"
    ]
}

{
  "module_name": "recorded_schemas",
  "module_type": "memory",
  "inputs_from": [
    "schema_recorder"
  ],
  "outputs_to": [
    "retraining_scheduler",
    "model_trainer",
    "sound_playback",
    "landmark_visualizer"
  ]
}



{
  "module_name": "retraining_scheduler",
  "module_type": "coordinator",
  "inputs_from": [
    "recorded_schemas",
    "feedback_log",
    "model_registry",
    "partner_ui"
  ],
  "outputs_to": [
    "model_trainer"
  ]
}



{
  "module_name": "schema_recorder",
  "module_type": "coordinator",
  "inputs_from": [
    "landmark_extractor",
    "input_broker",
    "audio_feed_worker",
    "session_manager"
  ],
  "outputs_to": [
    "recorded_schemas"
  ]
}

{
  "module_name": "session_manager",
  "module_type": "coordinator",
  "inputs_from": [
    "user",
    "partner_ui",
    "user_profile_store"
  ],
  "outputs_to": [
    "camera_feed_worker",
    "audio_feed_worker",
    "schema_recorder"
  ]
}


{
  "module_name": "sound_classifier",
  "module_type": "classifier",
  "inputs_from": [
    "audio_feed_worker",
    "model_registry"
  ],
  "outputs_to": [
    "input_broker"
  ]
}
{
  "module_name": "sound_playback",
  "module_type": "visualizer",
  "inputs_from": [
    "recorded_schemas"
  ],
  "outputs_to": [
    "partner_ui"
  ]
}

{
  "module_name": "speech_context_classifier",
  "module_type": "classifier",
  "inputs_from": [
    "speech_transcriber",
    "user_profile_store"
  ],
  "outputs_to": [
    "input_broker"
  ]
}
{
  "module_name": "speech_transcriber",
  "module_type": "worker",
  "inputs_from": [
    "audio_feed_worker"
  ],
  "outputs_to": [
    "speech_context_classifier"
  ]
}

{
  "module_name": "user",
  "module_type": "interface",
  "outputs_to": ["session_manager"]
}


{
  "module_name": "user_profile_store",
  "module_type": "memory",
  "inputs_from": [
    "partner_ui",
    "memory_interface"
  ],
  "outputs_to": [
    "clarification_planner",
    "output_expander",
    "output_planner",
    "llm_clarifier",
    "session_manager",
    "speech_context_classifier"
  ]
}
{
  "module_name": "visual_environment_classifier",
  "module_type": "classifier",
  "inputs_from": [
    "camera_feed_worker"
  ],
  "outputs_to": [
    "input_broker"
  ]
}
