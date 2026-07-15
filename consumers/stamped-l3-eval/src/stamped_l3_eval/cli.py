"""stamped-l3-eval CLI — corpus, backtest, artifact, lab-run."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from stamped_l3_eval.artifact import (
    GOLDEN_DIR,
    artifact_for_window,
    load_artifact,
    validate_artifact,
)


def _default_corpus() -> Path:
    return Path(__file__).resolve().parents[2] / "corpus" / "v0" / "windows.json"


def cmd_corpus_list(args: argparse.Namespace) -> int:
    corpus_path = Path(args.corpus)
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    for window in data["windows"]:
        print(f"{window['window_id']}\t{window['category']}\t{window['window']}")
    return 0


def cmd_backtest_run(args: argparse.Namespace) -> int:
    corpus_path = Path(args.corpus)
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    print(f"backtest run: corpus={corpus_path} windows={len(data['windows'])} (skeleton)")
    if args.shadow == "timesfm":
        print("timesfm shadow: not installed — pinball gate deferred (ADR-014)")
    return 0


def cmd_artifact_show(args: argparse.Namespace) -> int:
    data = load_artifact(args.path)
    dets = data["detections"]
    emitted = sum(1 for d in dets if d["status"] == "emitted")
    suppressed = sum(1 for d in dets if d["status"] == "suppressed")
    shadow = sum(1 for d in dets if d["status"] == "shadow_only")
    hypothesis = sum(1 for d in dets if d.get("status") == "hypothesis")
    l4 = sum(1 for d in dets if d.get("delivery") == "l4")
    lab_only = sum(1 for d in dets if d.get("delivery") == "lab_only")
    print(f"run_id={data['run_id']} window={data['window_id']} schema={data.get('schema_version')}")
    print(f"lanes: l4={l4} lab_only={lab_only}")
    print(
        f"detections: emitted={emitted} suppressed={suppressed} "
        f"shadow={shadow} hypothesis={hypothesis}"
    )
    for d in dets:
        delivery = d.get("delivery", "?")
        print(f"  [{delivery}/{d['status']}] {d['detector_kind']} {d['rule_or_model_ref']}")
    return 0


def cmd_lab_run(args: argparse.Namespace) -> int:
    """Produce or echo a RunArtifact for a corpus window.

    ponytail: when --from-core path missing, copy golden fixture / synthesize stub.
    Real engines stay in stamped-l3-core lab export (Phase D).
    """
    window_id = args.window
    runs_dir = Path(__file__).resolve().parents[2] / "artifacts" / "runs"
    out_dir = Path(args.out) if args.out else runs_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"run_{window_id}.json"

    if args.from_core:
        data = load_artifact(args.from_core)
        out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out_path} (from core export)")
        return 0

    existing = artifact_for_window(window_id)
    if existing and not args.force_stub:
        data = load_artifact(existing)
        print(f"using golden {existing}")
        print(f"detections={len(data['detections'])}")
        return 0

    # Minimal stub when no golden exists
    corpus = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    win = next((w for w in corpus["windows"] if w["window_id"] == window_id), None)
    if win is None:
        print(f"unknown window: {window_id}", file=sys.stderr)
        return 1
    stub = {
        "schema_version": "1.1.0",
        "run_id": f"run-{window_id}-stub",
        "window_id": window_id,
        "plant_id": win["plant_id"],
        "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "core_version": "0.0.0-stub",
        "rulepack_pins": [{"pack": "incomer", "version": "1.0.0"}],
        "inputs": {"source": "stub", "fixture_ref": win.get("rulepack_ref", "")},
        "detections": [
            {
                "detection_id": f"d-stub-{window_id}",
                "detector_kind": "engine",
                "rule_or_model_ref": win.get("rulepack_ref", "rulepack://incomer/1.0.0#unknown"),
                "category": win["category"],
                "status": "emitted",
                "delivery": "l4",
                "finding": None,
                "suppressions_checked": [],
                "scores": None,
                "logs": ["stub lab-run — replace via core lab export"],
            }
        ],
        "timeline": [
            {
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "step": "stub",
                "detail": "no core export",
            }
        ],
        "errors": [],
    }
    validate_artifact(stub)
    out_path.write_text(json.dumps(stub, indent=2) + "\n", encoding="utf-8")
    print(f"wrote stub {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stamped-l3-eval")
    sub = parser.add_subparsers(dest="command", required=True)

    corpus = sub.add_parser("corpus", help="Corpus commands")
    corpus_sub = corpus.add_subparsers(dest="corpus_cmd", required=True)
    list_parser = corpus_sub.add_parser("list", help="List corpus windows")
    list_parser.add_argument("--corpus", type=Path, default=_default_corpus())
    list_parser.set_defaults(func=cmd_corpus_list)

    backtest = sub.add_parser("backtest", help="Backtest commands")
    backtest_sub = backtest.add_subparsers(dest="backtest_cmd", required=True)
    run_parser = backtest_sub.add_parser("run", help="Run rolling backtest (skeleton)")
    run_parser.add_argument("--corpus", type=Path, default=_default_corpus())
    run_parser.add_argument("--shadow", choices=["timesfm", "none"], default="none")
    run_parser.set_defaults(func=cmd_backtest_run)

    artifact = sub.add_parser("artifact", help="RunArtifact commands")
    artifact_sub = artifact.add_subparsers(dest="artifact_cmd", required=True)
    show = artifact_sub.add_parser("show", help="Show and validate an artifact")
    show.add_argument("--path", type=Path, required=True)
    show.set_defaults(func=cmd_artifact_show)

    lab = sub.add_parser("lab-run", help="Produce RunArtifact for a window")
    lab.add_argument("--window", required=True)
    lab.add_argument("--corpus", type=Path, default=_default_corpus())
    lab.add_argument("--out", type=Path, default=None)
    lab.add_argument("--from-core", type=Path, default=None)
    lab.add_argument("--force-stub", action="store_true")
    lab.set_defaults(func=cmd_lab_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
