"""All tunable settings in one place. Values come from env vars / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"

VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "0")
CAMERA_NAME = os.getenv("CAMERA_NAME", "Demo Camera")
CAMERA_LOCATION = os.getenv("CAMERA_LOCATION", "Lab floor")
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "spillwatch.db"))

# --- Detection tuning (heuristic, Stage A). Record changes in PROGRESS.md. ---
BLUR_KERNEL = 21          # odd number
DIFF_THRESHOLD = 25       # 0-255 grayscale difference
MIN_AREA_PX = 1500        # ignore regions smaller than this
PERSIST_SECONDS = 3.0     # region must persist this long to become an incident
CLEAR_SECONDS = 5.0       # region must look clear this long -> awaiting_verification
REFERENCE_UPDATE_ALPHA = 0.01  # slow reference drift in non-spill areas
SAMPLE_FPS = 5            # frames per second to run detection on
