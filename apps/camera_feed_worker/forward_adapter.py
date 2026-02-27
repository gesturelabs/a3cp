import base64
import uuid

from apps.camera_feed_worker.repository import ForwardItem
from schemas import LandmarkExtractorFrameInput


def forward_item_to_landmark_input(item: ForwardItem) -> LandmarkExtractorFrameInput:
    frame_data_b64 = base64.b64encode(bytes(item.payload)).decode("ascii")

    return LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id=item.user_id,
        session_id=item.session_id,
        # BaseSchema.timestamp = message creation time; using frame event-time is acceptable here.
        timestamp=item.timestamp_frame,
        # ingest event
        event="capture.frame",
        modality="image",
        source="camera_feed_worker",
        # correlation
        capture_id=item.capture_id,
        seq=item.seq,
        timestamp_frame=item.timestamp_frame,
        # payload (raw base64 is fine)
        frame_data=frame_data_b64,
        # optional legacy field, omit unless needed
        # frame_id=record_id,
    )
