"""Lab export — full detection log for stamped-l3-eval Lab UI.

ponytail: in-memory store + stdlib HTTP handler; no FastAPI dependency.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from stamped_l3_core.detection_lane import assert_lane_invariant, delivery_for


class LabLog:
    """Accumulate detections (emitted, suppressed, shadow, hypothesis) for windows."""

    def __init__(self) -> None:
        self.core_version = "0.1.0"
        self.rulepack_pins: list[dict[str, str]] = []
        self.window_id = "live"
        self.plant_id = "unknown"
        self.run_id = "live-run"
        self.inputs: dict[str, Any] = {"source": "live"}
        self.detections: list[dict[str, Any]] = []
        self.timeline: list[dict[str, str]] = []
        self.errors: list[str] = []
        self.started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def reset(self, *, window_id: str, plant_id: str, run_id: str | None = None) -> None:
        self.window_id = window_id
        self.plant_id = plant_id
        self.run_id = run_id or f"live-{window_id}"
        self.detections.clear()
        self.timeline.clear()
        self.errors.clear()
        self.started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def add_timeline(self, step: str, detail: str) -> None:
        self.timeline.append(
            {
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "step": step,
                "detail": detail,
            }
        )

    def add_detection(
        self,
        *,
        detection_id: str,
        detector_kind: str,
        rule_or_model_ref: str,
        category: str,
        status: str,
        suppressions_checked: list[str] | None = None,
        finding: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        logs: list[str] | None = None,
        delivery: str | None = None,
    ) -> None:
        lane = delivery if delivery is not None else delivery_for(status)
        assert_lane_invariant(status, lane)
        self.detections.append(
            {
                "detection_id": detection_id,
                "detector_kind": detector_kind,
                "rule_or_model_ref": rule_or_model_ref,
                "category": category,
                "status": status,
                "delivery": lane,
                "finding": finding,
                "suppressions_checked": suppressions_checked or [],
                "scores": scores,
                "logs": logs or [],
            }
        )
        self.add_timeline(f"{detector_kind}.{category}", f"{lane}/{status}")

    def to_run_artifact(self) -> dict[str, Any]:
        return {
            "schema_version": "1.1.0",
            "run_id": self.run_id,
            "window_id": self.window_id,
            "plant_id": self.plant_id,
            "started_at": self.started_at,
            "core_version": self.core_version,
            "rulepack_pins": list(self.rulepack_pins),
            "inputs": dict(self.inputs),
            "detections": list(self.detections),
            "timeline": list(self.timeline),
            "errors": list(self.errors),
        }


_LAB = LabLog()


def get_lab_log() -> LabLog:
    return _LAB


def export_run_artifact() -> dict[str, Any]:
    return get_lab_log().to_run_artifact()


def seed_demo_lab() -> LabLog:
    """Populate a demo live snapshot for local attach testing."""
    lab = get_lab_log()
    lab.reset(window_id="live-demo", plant_id="plant_ghaziabad_1", run_id="live-demo-001")
    lab.rulepack_pins = [{"pack": "incomer", "version": "1.0.0"}]
    lab.inputs = {"source": "lab_seed"}
    lab.add_detection(
        detection_id="live-md-1",
        detector_kind="engine",
        rule_or_model_ref="rulepack://incomer/1.0.0#md_overlap",
        category="md_overlap",
        status="emitted",
        finding={"finding_id": "f-live-md", "category": "md_overlap"},
        suppressions_checked=["startup_window"],
        scores={"peak_kva": 1010},
        logs=["live demo emit"],
    )
    lab.add_detection(
        detection_id="live-md-supp",
        detector_kind="rule",
        rule_or_model_ref="rulepack://load_management/1.0.0#stagger_costart",
        category="md_overlap",
        status="suppressed",
        suppressions_checked=["startup_window"],
        logs=["live demo suppress"],
    )
    lab.add_detection(
        detection_id="live-hypothesis",
        detector_kind="rule",
        rule_or_model_ref="rulepack://attribution/1.0.0#costart_window",
        category="md_overlap",
        status="hypothesis",
        scores={"rank": 2, "ramp_kw": 40, "hops": 2, "proximity": 0.333, "score": 13.3},
        logs=["live demo runner-up lab_only"],
    )
    lab.add_detection(
        detection_id="live-shadow",
        detector_kind="ml_shadow",
        rule_or_model_ref="mlflow://timesfm/shadow#md_exceedance",
        category="md_exceedance_risk",
        status="shadow_only",
        scores={"p90": 960},
        logs=["live demo shadow"],
    )
    lab.add_detection(
        detection_id="live-attr-shadow",
        detector_kind="ml_shadow",
        rule_or_model_ref="shadow://attribution/rank_ablation_corr_primary",
        category="md_overlap",
        status="shadow_only",
        scores={
            "shadow_method": "rank_ablation_corr_primary",
            "agree_with_primary": True,
            "primary_rank_ref": "furnace-a",
        },
        logs=["live demo ADR-016 ablation"],
    )
    return lab


class LabExportHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # quieter
        return

    def _unauthorized(self) -> None:
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"unauthorized"}')

    def _ok(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/lab/export":
            self.send_response(404)
            self.end_headers()
            return
        token = os.environ.get("CORE_LAB_TOKEN", "")
        if token:
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                self._unauthorized()
                return
        self._ok(export_run_artifact())


def serve_lab(host: str = "127.0.0.1", port: int = 8090) -> ThreadingHTTPServer:
    seed_demo_lab()
    server = ThreadingHTTPServer((host, port), LabExportHandler)
    return server


def main() -> None:
    host = os.environ.get("CORE_LAB_HOST", "127.0.0.1")
    port = int(os.environ.get("CORE_LAB_PORT", "8090"))
    srv = serve_lab(host, port)
    print(f"lab export listening on http://{host}:{port}/lab/export")
    srv.serve_forever()


if __name__ == "__main__":
    main()
