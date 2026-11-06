"""Mask out people/objects using a PRETRAINED YOLO detector (Ultralytics).

TODO (Phase 3): load yolov8n.pt (or current nano), run on the frame with
device="mps", return a uint8 mask that is 255 inside each person/object box
(slightly dilated). SpillDetector.detect() takes this as ignore_mask.
"""
import numpy as np


def person_mask(frame: np.ndarray) -> np.ndarray:
    """Placeholder: masks nothing until Phase 3."""
    return np.zeros(frame.shape[:2], dtype=np.uint8)
