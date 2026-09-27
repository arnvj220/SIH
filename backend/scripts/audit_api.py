"""backend/scripts/audit_api.py — corrected to run the lifespan."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

PROBES = [
    ("GET",  "/health", None),
    ("GET",  "/api/attacks", None),
    ("GET",  "/api/alerts", None),
    ("GET",  "/api/events", None),
]

print("=" * 72)
print("HTTP probes against the running app (TestClient with lifespan)")
print("=" * 72)

with TestClient(app) as client:          # triggers startup → ensure MongoDB indexes
    for method, path, body in PROBES:
        r = client.request(method, path, json=body)
        marker = "OK  " if r.status_code < 500 else "FAIL"
        print(f"{marker} {method:<5} {path:<32} -> {r.status_code}")

    print()
    print("=" * 72)
    print("OpenAPI schema — all registered routes")
    print("=" * 72)
    schema = client.get("/openapi.json").json()
    for path in sorted(schema["paths"].keys()):
        methods = sorted(m.upper() for m in schema["paths"][path].keys())
        print(f"{','.join(methods):<20} {path}")