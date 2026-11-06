"""SQLite incident store. Statuses follow the lifecycle in CLAUDE.md."""
import sqlite3
from datetime import datetime, timezone

from backend.app import config

STATUSES = ["new", "acknowledged", "cleaning", "awaiting_verification", "resolved"]

# Allowed status changes. awaiting_verification can go back to cleaning if staff reject it.
TRANSITIONS = {
    "new": {"acknowledged"},
    "acknowledged": {"cleaning"},
    "cleaning": {"awaiting_verification"},
    "awaiting_verification": {"resolved", "cleaning"},
    "resolved": set(),
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_name TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    snapshot_path TEXT,
    bbox TEXT NOT NULL,          -- JSON [x, y, w, h]
    contour TEXT,                -- JSON [[x, y], ...]
    pixel_area REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def create_incident(conn, camera_name, location, bbox_json, pixel_area,
                    snapshot_path=None, contour_json=None) -> int:
    ts = now()
    cur = conn.execute(
        "INSERT INTO incidents (camera_name, location, created_at, updated_at, snapshot_path,"
        " bbox, contour, pixel_area) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (camera_name, location, ts, ts, snapshot_path, bbox_json, contour_json, pixel_area),
    )
    conn.commit()
    return cur.lastrowid


def list_incidents(conn, status: str | None = None) -> list[dict]:
    if status:
        rows = conn.execute("SELECT * FROM incidents WHERE status = ? ORDER BY id DESC", (status,))
    else:
        rows = conn.execute("SELECT * FROM incidents ORDER BY id DESC")
    return [dict(r) for r in rows]


def get_incident(conn, incident_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return dict(row) if row else None


def set_status(conn, incident_id: int, new_status: str) -> dict:
    inc = get_incident(conn, incident_id)
    if inc is None:
        raise KeyError(incident_id)
    if new_status not in TRANSITIONS[inc["status"]]:
        raise ValueError(f"Cannot go from {inc['status']} to {new_status}")
    ts = now()
    resolved_at = ts if new_status == "resolved" else None
    conn.execute(
        "UPDATE incidents SET status = ?, updated_at = ?, resolved_at = COALESCE(?, resolved_at)"
        " WHERE id = ?",
        (new_status, ts, resolved_at, incident_id),
    )
    conn.commit()
    return get_incident(conn, incident_id)
