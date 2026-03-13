import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

image_bgr = cv2.imread("apps/landmark_extractor/images/image1.jpg")
assert image_bgr is not None
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

pose = vision.PoseLandmarker.create_from_options(
    vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path="models/mediapipe/pose_landmarker.task"
        )
    )
)

hand = vision.HandLandmarker.create_from_options(
    vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path="models/mediapipe/hand_landmarker.task"
        )
    )
)

face = vision.FaceLandmarker.create_from_options(
    vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path="models/mediapipe/face_landmarker.task"
        )
    )
)

pose_result = pose.detect(mp_image)
hand_result = hand.detect(mp_image)
face_result = face.detect(mp_image)

print("pose count:", len(pose_result.pose_landmarks))
print("hand count:", len(hand_result.hand_landmarks))
print("handedness:", hand_result.handedness)
print("face count:", len(face_result.face_landmarks))

if pose_result.pose_landmarks:
    print("pose landmarks:", len(pose_result.pose_landmarks[0]))

if hand_result.hand_landmarks:
    print("hand landmarks:", len(hand_result.hand_landmarks[0]))

if face_result.face_landmarks:
    print("face landmarks:", len(face_result.face_landmarks[0]))
