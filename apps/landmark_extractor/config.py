# apps/landmark_extractor/config.py

"""
apps.landmark_extractor.config

Extractor configuration and constants for the Landmark Extractor MVP.

This module defines deterministic configuration used for:
- MediaPipe Tasks model, running-mode, and detector configuration
- Landmark selection
- Feature layout construction
- Feature artifact encoding

Constraints:
- constants only
- no runtime logic
- no filesystem IO
"""


# ------------------------------------------------------------
# MediaPipe Tasks configuration (MVP)
# ------------------------------------------------------------


MEDIAPIPE_RUNNING_MODE = "VIDEO"

POSE_LANDMARKER_MODEL_PATH = "models/mediapipe/pose_landmarker.task"
HAND_LANDMARKER_MODEL_PATH = "models/mediapipe/hand_landmarker.task"
FACE_LANDMARKER_MODEL_PATH = "models/mediapipe/face_landmarker.task"

POSE_MAX_RESULTS = 1
HAND_MAX_NUM_HANDS = 2
FACE_MAX_NUM_FACES = 1

# ------------------------------------------------------------
# Landmark selection contract
# ------------------------------------------------------------

INCLUDE_POSE_LANDMARKS = True
INCLUDE_LEFT_HAND_LANDMARKS = True
INCLUDE_RIGHT_HAND_LANDMARKS = True
INCLUDE_FACE_LANDMARKS = True
USE_REDUCED_FACE_SUBSET = True

USE_FULL_POSE_LANDMARK_SET = True
POSE_LANDMARK_COUNT = 33

USE_FULL_LEFT_HAND_LANDMARK_SET = True
USE_FULL_RIGHT_HAND_LANDMARK_SET = True
HAND_LANDMARK_COUNT = 21

FACE_SUBSET_COMPONENTS = (
    "left_eyebrow",
    "right_eyebrow",
    "left_eye",
    "right_eye",
    "left_iris",
    "right_iris",
    "nose",
    "mouth",
    "chin",
)

FACE_MESH_BASE_LANDMARK_COUNT = 468
FACE_MESH_LANDMARK_COUNT_WITH_IRISES = 478

# Reduced expressive face subset used by MVP feature extraction.
# Explicit MediaPipe FaceMesh landmark indices in deterministic order.
FACE_LANDMARK_INDICES = [
    # left iris
    468,
    469,
    470,
    471,
    # right iris
    472,
    473,
    474,
    475,
    # left eye contour
    33,
    133,
    159,
    145,
    # right eye contour
    263,
    362,
    386,
    374,
    # left eyebrow
    70,
    63,
    105,
    # right eyebrow
    336,
    296,
    334,
    # nose anchors
    1,
    6,
    197,
    # mouth landmarks
    61,
    291,
    13,
    14,
    78,
    308,
    # chin
    199,
]

FACE_LANDMARK_COUNT = len(FACE_LANDMARK_INDICES)

# Ordered landmark identifiers used to build feature rows
# (deterministic column ordering)
ORDERED_LANDMARKS = (
    # pose landmarks
    *[("pose", i) for i in range(POSE_LANDMARK_COUNT)],
    # left hand landmarks
    *[("left_hand", i) for i in range(HAND_LANDMARK_COUNT)],
    # right hand landmarks
    *[("right_hand", i) for i in range(HAND_LANDMARK_COUNT)],
    # reduced face subset
    *[("face", i) for i in FACE_LANDMARK_INDICES],
)

# ------------------------------------------------------------
# Feature layout configuration
# ------------------------------------------------------------

# Coordinates persisted per landmark
FEATURE_COORDS_PER_LANDMARK = 2

# Coordinate names (order matters)
FEATURE_COORD_NAMES = ("x", "y")

# z is excluded from MVP
FEATURE_INCLUDE_Z = False

# Derived feature constants
LANDMARK_COUNT = len(ORDERED_LANDMARKS)
FEATURE_DIM = LANDMARK_COUNT * FEATURE_COORDS_PER_LANDMARK

# ------------------------------------------------------------
# Encoding and artifact configuration
# ------------------------------------------------------------

# Identifier emitted in raw_features_ref.encoding
FEATURE_ENCODING_ID = "mediapipe_tasks_video_xy_v1"

# Artifact format
FEATURE_ARTIFACT_FORMAT = "npz"

# Feature dtype used in stored matrix
FEATURE_DTYPE = "float32"

# ------------------------------------------------------------
# Missing landmark encoding
# ------------------------------------------------------------

MISSING_LANDMARK_X = 0.0
MISSING_LANDMARK_Y = 0.0
MISSING_LANDMARK_PAIR = (MISSING_LANDMARK_X, MISSING_LANDMARK_Y)
