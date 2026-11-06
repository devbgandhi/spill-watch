# Spill Watch API contract

Backend base URL (dev): `http://localhost:8000`. Frontend dev server: `http://localhost:5173`.

## Incident object

```json
{
  "id": 1,
  "camera_name": "Demo Camera",
  "location": "Lab floor",
  "created_at": "2026-11-06T13:00:00+00:00",
  "updated_at": "2026-11-06T13:00:00+00:00",
  "resolved_at": null,
  "snapshot_path": "incident_1.jpg",
  "bbox": "[120, 200, 80, 60]",
  "contour": null,
  "pixel_area": 3400.0,
  "status": "new"
}
```

`bbox` and `contour` are JSON strings. Snapshot image URL: `/snapshots/<snapshot_path>`.

## Statuses and allowed transitions

```
new → acknowledged → cleaning → awaiting_verification → resolved
                                 awaiting_verification → cleaning   (staff reject)
```

`cleaning → awaiting_verification` is normally set **by the detector** when the region looks clear.

UI wording: show "Suspected spill" until a human confirms. Show
"Visually clear: awaiting staff confirmation" for `awaiting_verification`. Never say "safe".

## Endpoints

| Method | Path | Status | Notes |
|---|---|---|---|
| GET | `/api/health` | working | `{ok, camera}` |
| GET | `/api/incidents?status=new` | working | newest first, `status` optional |
| GET | `/api/incidents/{id}` | working | 404 if missing |
| PATCH | `/api/incidents/{id}` | working | body `{"status": "acknowledged"}`; 409 on illegal transition |
| GET | `/stream` | TODO | MJPEG live feed with overlays, use in `<img src>` |
| WS | `/ws` | TODO | pushes `{"type": "incident_created" \| "incident_updated", "incident": {...}}` |
