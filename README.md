# Spill Watch

AI that catches spills on existing CCTV before someone slips.

Spill Watch watches a floor zone through an existing camera, flags suspected liquid spills,
alerts staff on a dashboard, and checks whether the area looks visually clear after cleaning.
A human always confirms before an incident is resolved.

> Hackathon prototype. The current detector is a **heuristic** (frame differencing against a
> dry-floor reference). People are masked out by a **pretrained** YOLO detector. A trained
> spill segmentation model is planned and not yet built.

## Run

Requires Python 3.12 and Node.

```bash
# Backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
python -m backend.tools.check_setup      # versions + MPS check
python -m backend.tools.live_test        # OpenCV detector window
uvicorn backend.app.main:app --reload    # API on :8000

# Frontend
cd frontend && npm install && npm run dev   # :5173
```

API contract: [docs/api.md](docs/api.md).

## Privacy

Detects floor hazards, not people. No face recognition and no tracking of individuals.
Keep camera credentials in `.env` (git-ignored).
