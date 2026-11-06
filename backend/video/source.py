"""One video pipeline, three sources: webcam index, MP4 path, or RTSP URL."""
import cv2


def open_source(source: str | int) -> cv2.VideoCapture:
    """Open a webcam ("0", "1"), a video file path, or an rtsp:// URL."""
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        # Don't print the raw source: RTSP URLs can contain credentials.
        raise RuntimeError("Could not open video source (check VIDEO_SOURCE in .env)")
    return cap
