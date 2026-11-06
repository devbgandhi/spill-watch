"""Insert a fake incident so the dashboard can be built before detection works.
Run from the repo root: python -m backend.tools.seed_incident
"""
import json

from backend.app import config, db

conn = db.connect()
iid = db.create_incident(conn, config.CAMERA_NAME, config.CAMERA_LOCATION,
                         json.dumps([120, 200, 80, 60]), 3400.0)
print("Created test incident", iid)
