{
    "module_name": "audio_feed_worker",
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
    "inputs_from": [
        "recorded_schemas"
    ],
    "outputs_to": [
      "partner_ui"
    ]
}

{
    "module_name": "llm_clarifier",
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
    "inputs_from": [
        "memory_interface"
    ],
    "outputs_to": [
        "confidence_evaluator"
    ]
}

{
    "module_name": "memory_interface",
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
    "inputs_from": [
        "output_planner",
        "landmark_visualizer",
        "sound_playback",
        "llm_clarifier",
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
  "inputs_from": [
    "recorded_schemas"
  ],
  "outputs_to": [
    "partner_ui"
  ]
}

{
  "module_name": "speech_context_classifier",
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
  "inputs_from": [
    "audio_feed_worker"
  ],
  "outputs_to": [
    "speech_context_classifier"
  ]
}

{
  "module_name": "user_profile_store",
  "inputs_from": [
    "partner_ui",
    "memory_interface"
  ],
  "outputs_to": [
    "clarification_planner",
    "output_expander",
    "output_planner",
    "llm_clarifier",
    "session_manager"
  ]
}
{
  "module_name": "visual_environment_classifier",
  "inputs_from": [
    "camera_feed_worker",
  ],
  "outputs_to": [
    "input_broker"
  ]
}
