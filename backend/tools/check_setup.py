"""Phase 1 check. Run from the repo root: python -m backend.tools.check_setup"""
import sys

print("Python", sys.version.split()[0])
import cv2
print("OpenCV", cv2.__version__)
import torch
print("PyTorch", torch.__version__, "| MPS available:", torch.backends.mps.is_available())
import ultralytics
print("Ultralytics", ultralytics.__version__)
