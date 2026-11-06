"""Stage A spill detector. HEURISTIC, NOT AI: frame differencing against a dry-floor reference.

Pipeline: grayscale + blur -> absdiff vs reference -> threshold -> morphology
-> contours -> min-area filter. People/objects are masked out separately
(person_mask.py, pretrained YOLO) before contours are accepted.
"""
from dataclasses import dataclass

import cv2
import numpy as np

from backend.app import config


@dataclass
class Region:
    bbox: tuple[int, int, int, int]  # x, y, w, h in full-frame coordinates
    area: float                      # pixel area of the contour
    contour: np.ndarray


class SpillDetector:
    def __init__(self, zone: tuple[int, int, int, int] | None = None):
        self.zone = zone              # x, y, w, h; None = whole frame
        self.reference: np.ndarray | None = None

    def _prep(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        k = config.BLUR_KERNEL
        return cv2.GaussianBlur(gray, (k, k), 0)

    def set_reference(self, frame: np.ndarray) -> None:
        """Capture the dry-floor baseline (the 'B' key in live_test.py)."""
        self.reference = self._prep(frame).astype(np.float32)

    def detect(self, frame: np.ndarray, ignore_mask: np.ndarray | None = None) -> tuple[list[Region], np.ndarray]:
        """Return suspected spill regions and the binary mask.

        ignore_mask: uint8, 255 where people/objects are (excluded from detection).
        """
        cur = self._prep(frame)
        if self.reference is None:
            return [], np.zeros_like(cur)

        diff = cv2.absdiff(cur, cv2.convertScaleAbs(self.reference))
        _, mask = cv2.threshold(diff, config.DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        if self.zone is not None:
            x, y, w, h = self.zone
            zone_mask = np.zeros_like(mask)
            zone_mask[y:y + h, x:x + w] = 255
            mask = cv2.bitwise_and(mask, zone_mask)
        if ignore_mask is not None:
            mask = cv2.bitwise_and(mask, cv2.bitwise_not(ignore_mask))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        regions = [
            Region(bbox=cv2.boundingRect(c), area=cv2.contourArea(c), contour=c)
            for c in contours
            if cv2.contourArea(c) >= config.MIN_AREA_PX
        ]

        # Absorb slow lighting drift, but only where nothing suspicious is happening.
        cv2.accumulateWeighted(cur, self.reference, config.REFERENCE_UPDATE_ALPHA,
                               mask=cv2.bitwise_not(mask))
        return regions, mask
