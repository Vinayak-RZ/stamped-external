"""Live client against a stdlib mock of core /lab/export."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from stamped_l3_eval.live_client import fetch_live_snapshot

PAYLOAD = {
    "schema_version": "1.1.0",
    "run_id": "mock-live",
    "window_id": "live-demo",
    "plant_id": "plant_ghaziabad_1",
    "started_at": "2026-07-14T00:00:00Z",
    "core_version": "0.1.0",
    "rulepack_pins": [{"pack": "incomer", "version": "1.0.0"}],
    "inputs": {"source": "mock"},
    "detections": [
        {
            "detection_id": "d1",
            "detector_kind": "engine",
            "rule_or_model_ref": "rulepack://incomer/1.0.0#md_overlap",
            "category": "md_overlap",
            "status": "emitted",
            "delivery": "l4",
            "finding": None,
            "suppressions_checked": [],
            "scores": None,
            "logs": ["mock"],
        }
    ],
    "timeline": [],
    "errors": [],
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/lab/export":
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(PAYLOAD).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def test_fetch_live_snapshot_roundtrip() -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", 18091), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        data = fetch_live_snapshot(url="http://127.0.0.1:18091", token="", timeout=2.0)
        assert data["run_id"] == "mock-live"
        assert data["detections"][0]["status"] == "emitted"
    finally:
        srv.shutdown()
