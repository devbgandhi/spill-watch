"""FastAPI backend. Run from the repo root:
    uvicorn backend.app.main:app --reload
API contract for the frontend lives in docs/api.md.

TODO (Phase 5): GET /stream (MJPEG with overlays), WS /ws (incident events).
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app import config, db

app = FastAPI(title="Spill Watch")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/snapshots", StaticFiles(directory=config.SNAPSHOT_DIR), name="snapshots")

conn = db.connect()


class StatusUpdate(BaseModel):
    status: str


@app.get("/api/health")
def health():
    return {"ok": True, "camera": config.CAMERA_NAME}


@app.get("/api/incidents")
def incidents(status: str | None = None):
    return db.list_incidents(conn, status)


@app.get("/api/incidents/{incident_id}")
def incident(incident_id: int):
    inc = db.get_incident(conn, incident_id)
    if inc is None:
        raise HTTPException(404, "Incident not found")
    return inc


@app.patch("/api/incidents/{incident_id}")
def update_status(incident_id: int, body: StatusUpdate):
    if body.status not in db.STATUSES:
        raise HTTPException(400, f"Unknown status: {body.status}")
    try:
        return db.set_status(conn, incident_id, body.status)
    except KeyError:
        raise HTTPException(404, "Incident not found")
    except ValueError as e:
        raise HTTPException(409, str(e))
