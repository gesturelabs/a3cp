import base64

from apps.camera_feed_worker.repository import ForwardItem
from schemas import LandmarkExtractorInput


def forward_item_to_landmark_input(item: ForwardItem) -> LandmarkExtractorInput:
    frame_data_b64 = base64.b64encode(bytes(item.payload)).decode("ascii")

    return LandmarkExtractorInput(
        frame_id=f"{item.capture_id}:{item.seq}",
        timestamp=item.timestamp_frame.isoformat(),  # required
        session_id=item.session_id,
        user_id=item.user_id,
        modality="vision",
        source="camera_feed_worker",
        frame_data=frame_data_b64,
    )
