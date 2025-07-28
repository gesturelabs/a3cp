import base64
from io import BytesIO

from fastapi import APIRouter, HTTPException
from PIL import Image

from schemas.landmark_extractor.landmark_extractor import (
    LandmarkExtractorInput,
    LandmarkExtractorOutput,
)

router = APIRouter()


def decode_base64_image(data_url: str) -> Image.Image:
    """
    Decode base64-encoded image data from a data URL or raw base64 string.
    Returns a PIL Image in RGB format.
    """
    if "," in data_url:
        _, base64_data = data_url.split(",", 1)
    else:
        base64_data = data_url

    try:
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image decode failed: {e}") from e


@router.post("/", response_model=LandmarkExtractorOutput)
def extract_landmarks(input_data: LandmarkExtractorInput) -> LandmarkExtractorOutput:
    """
    Landmark extractor endpoint (stub).
    Decodes image from input and returns placeholder landmark vector.
    """
    _ = decode_base64_image(input_data.frame_data)

    # TODO: Replace with real MediaPipe logic
    return LandmarkExtractorOutput(**LandmarkExtractorOutput.example_output())
