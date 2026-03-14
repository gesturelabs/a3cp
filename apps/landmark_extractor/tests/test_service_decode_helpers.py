# apps/landmark_extractor/tests/test_service_decode_helpers.py
import pytest

from apps.landmark_extractor import service


# test_strip_data_url_prefix_returns_raw_base64_for_data_url
def test_strip_data_url_prefix_returns_raw_base64_for_data_url():
    data_url = "data:image/jpeg;base64,ZmFrZUJhc2U2NA=="

    result = service._strip_data_url_prefix(data_url)

    assert result == "ZmFrZUJhc2U2NA=="


# test_strip_data_url_prefix_returns_input_when_no_prefix
def test_strip_data_url_prefix_returns_input_when_no_prefix():
    raw_base64 = "ZmFrZUJhc2U2NA=="

    result = service._strip_data_url_prefix(raw_base64)

    assert result == raw_base64


# test_strip_data_url_prefix_raises_for_invalid_data_url
def test_strip_data_url_prefix_raises_for_invalid_data_url():
    invalid_data_url = "data:image/jpeg;base64"  # missing comma separator

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._strip_data_url_prefix(invalid_data_url)


# test_decode_base64_bytes_decodes_valid_base64
def test_decode_base64_bytes_decodes_valid_base64():
    data = "aGVsbG8="  # base64 for "hello"

    result = service._decode_base64_bytes(data)

    assert isinstance(result, bytes)
    assert result == b"hello"


# test_decode_base64_bytes_raises_for_invalid_base64
def test_decode_base64_bytes_raises_for_invalid_base64():
    invalid_base64 = "not-valid-base64!!"

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._decode_base64_bytes(invalid_base64)


# test_bytes_to_frame_raises_when_opencv_returns_none


def test_bytes_to_frame_raises_when_opencv_returns_none(monkeypatch):
    monkeypatch.setattr(service.cv2, "imdecode", lambda *args, **kwargs: None)

    fake_bytes = b"not-an-image"

    with pytest.raises(service.LandmarkExtractorFrameError):
        service._bytes_to_frame(fake_bytes)


# test_decode_frame_data_decodes_raw_base64_image
def test_decode_frame_data_decodes_raw_base64_image(monkeypatch):
    expected_frame = object()

    monkeypatch.setattr(service, "_strip_data_url_prefix", lambda v: v)
    monkeypatch.setattr(service, "_decode_base64_bytes", lambda v: b"bytes")
    monkeypatch.setattr(service, "_bytes_to_frame", lambda v: expected_frame)

    result = service._decode_frame_data("ZmFrZQ==")

    assert result is expected_frame


# test_decode_frame_data_decodes_data_url_image
def test_decode_frame_data_decodes_data_url_image(monkeypatch):
    expected_frame = object()

    called = {"strip": False}

    def fake_strip_data_url_prefix(v):
        called["strip"] = True
        return "ZmFrZQ=="

    monkeypatch.setattr(service, "_strip_data_url_prefix", fake_strip_data_url_prefix)
    monkeypatch.setattr(service, "_decode_base64_bytes", lambda v: b"bytes")
    monkeypatch.setattr(service, "_bytes_to_frame", lambda v: expected_frame)

    result = service._decode_frame_data("data:image/jpeg;base64,ZmFrZQ==")

    assert called["strip"] is True
    assert result is expected_frame
