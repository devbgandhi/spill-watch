"""Phase 2: standalone live detector (OpenCV windows).
Run from the repo root: python -m backend.tools.live_test

Keys: drag mouse = select zone, B = capture dry-floor baseline, Q = quit.
"""
import cv2

from backend.app import config
from backend.detection.detector import SpillDetector
from backend.detection.person_mask import person_mask
from backend.video.source import open_source

WIN = "Spill Watch (heuristic)"
drag = {"start": None, "zone": None}


def on_mouse(event, x, y, flags, _):
    if event == cv2.EVENT_LBUTTONDOWN:
        drag["start"] = (x, y)
    elif event == cv2.EVENT_LBUTTONUP and drag["start"]:
        x0, y0 = drag["start"]
        w, h = abs(x - x0), abs(y - y0)
        if w > 10 and h > 10:
            drag["zone"] = (min(x, x0), min(y, y0), w, h)
        drag["start"] = None


def main():
    cap = open_source(config.VIDEO_SOURCE)
    det = SpillDetector()
    cv2.namedWindow(WIN)
    cv2.setMouseCallback(WIN, on_mouse)

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        det.zone = drag["zone"]
        regions, mask = det.detect(frame, ignore_mask=person_mask(frame))

        view = frame.copy()
        if det.zone:
            x, y, w, h = det.zone
            cv2.rectangle(view, (x, y), (x + w, y + h), (255, 200, 0), 2)
        cv2.drawContours(view, [r.contour for r in regions], -1, (0, 0, 255), 2)
        if det.reference is None:
            cv2.putText(view, "Press B on a DRY floor to capture baseline", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        elif regions:
            cv2.rectangle(view, (0, 0), (view.shape[1], 40), (0, 0, 255), -1)
            cv2.putText(view, "POSSIBLE SPILL (heuristic)", (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow(WIN, view)
        cv2.imshow("mask", mask)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("b"):
            det.set_reference(frame)
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
