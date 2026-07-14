"""CLI lab-run / artifact show smoke tests."""

from __future__ import annotations

from pathlib import Path

from stamped_l3_eval.cli import main

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "artifacts" / "golden" / "run_w-md-001.json"


def test_artifact_show(capsys) -> None:
    rc = main(["artifact", "show", "--path", str(GOLDEN)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "emitted=" in out
    assert "md_overlap" in out


def test_lab_run_uses_golden(capsys) -> None:
    rc = main(["lab-run", "--window", "w-md-001"])
    assert rc == 0
    assert "detections=" in capsys.readouterr().out
