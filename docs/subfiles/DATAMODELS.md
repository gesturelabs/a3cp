
--------------------------------------------------------------- 
This is the canonical schema used across A3CP modules including 
Streamer, Trainer, Inference, CARE Engine, and Feedback Logger. 
 
Field Name               | Type     | Req | Description                                      | Example 
------------------------|----------|-----|--------------------------------------------------|------------------------------- 
schema_version           | string   | ✅  | Version of the schema                            | "1.1.0" 
record_id                | UUID     | ✅  | Unique ID for this record                        | "uuid-1234-5678-9012" 
user_id                  | string   | ✅  | Pseudonymous user identifier                     | "elias01" 
session_id               | string   | ✅  | Group ID for the session                         | "a3cp_sess_2025-05-05_elias01" 
stream_segment_id        | string   | ❌  | Optional stream window                           | "elias01_2025-05-05T12:31:45Z" 
sequence_id              | string   | ❌  | Step-wise frame/utterance number                 | "elias01_000023" 
frame_index              | integer  | ❌  | Index of frame in sequence                       | 23 
timestamp                | datetime | ✅  | UTC ISO 8601 timestamp                           | "2025-05-05T12:31:46.123Z" 
 
modality                 | string   | ✅  | Input type: gesture, audio, etc.                 | "gesture" 
source                   | string   | ✅  | Who produced the input                           | "communicator" 
intent_label             | string   | ❌  | User-assigned intent                             | "help" 
label_status             | string   | ❌  | Label state: confirmed/unconfirmed/corrected     | "unconfirmed" 
classifier_output        | object   | ❌  | Model result and confidence                      | { "intent": "eat", "confidence": 0.91 } 
label_correction         | string   | ❌  | Override label from caregiver                    | null 
 
context.location         | string   | ❌  | Location tag                                     | "kitchen" 
context.prompt_type      | string   | ❌  | Type of communication prompt                     | "natural_use" 
context.partner_speech   | string   | ❌  | Spoken prompt by partner                         | "Are you hungry?" 
context.session_notes    | string   | ❌  | Freeform caregiver notes                         | null 
 
consent_given            | boolean  | ❌  | Whether consent was recorded                     | true 
is_demo                  | boolean  | ❌  | Was this a test/demo record                      | false 
device_id                | string   | ❌  | Device used to record input                      | "jetson_nano_01" 
vector_version           | string   | ❌  | Version of the vector encoder                    | "v2.1" 
 
vector                   | float[]  | ❌ | Numerical representation of input (maybe pointer) | [0.646233, 0.581001, ...] 
data_path                | string   | ❌  | File path to original .wav/.parquet              | "/data/elias01/gesture.parquet" 
output_mode              | string   | ❌  | (Future) Mode of AAC output                      | null 
output_phrase            | string   | ❌  | (Future) Phrase to be rendered                   | null 
-- New Fields in v1.2 -- 
------------------------------------------------------------ 
context.topic_tag        | string   | ❌  | 🆕 Topic derived from partner speech (e.g., "food") 
context.relevance_score  | float    | ❌  | 🆕 Score expressing how relevant the transcript is to likely intents 
context.flags            | object   | ❌  | 🆕 Structured flags (e.g., {"question_detected": true}) 
ASR_confidence_score     | float    | ❌  | 🆕 Confidence level of automated speech transcription 
raw_features_ref         | string   | ❌  | 🆕 Pointer or hash reference to source vector/mfcc for reproducibility 
final_decision           | string   | ❌  | 🆕 Clarified or selected output intent (if resolution module is used) 
output_type              | string   | ❌  | 🆕 What kind of output is being delivered (e.g., "intent", "clarification") 
-- New Fields in v1.3 (Memory Outputs) -- 
------------------------------------------------------------ 
memory.intent_boosts     | object     | ❌  | 🆕 Dictionary of user-specific intent weightings (e.g., {"eat": 0.15}) 
memory.fallback_suggestions | list    | ❌  | 🆕 Ranked list of fallback intents from memory (e.g., ["rest", "drink"]) 
memory.hint_used         | boolean    | ❌  | 🆕 Whether memory advice influenced the current decision
