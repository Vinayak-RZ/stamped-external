"""CLI smoke tests for stamped-l3-eval."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from stamped_l3_eval.cli import main

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "v0" / "windows.json"


def test_corpus_list_prints_windows(capsys):
    rc = main(["corpus", "list", "--corpus", str(CORPUS)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "w-md-001" in out
    assert "md_overlap" in out


def test_backtest_run_skeleton(capsys):
    rc = main(["backtest", "run", "--corpus", str(CORPUS)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "backtest run" in out
    assert "windows=3" in out


def test_corpus_has_three_windows():
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert len(data["windows"]) == 3


@pytest.mark.skipif(
    subprocess.run(["which", "stamped-l3-eval"], capture_output=True).returncode != 0,
    reason="console script not installed",
)
def test_console_script_installed():
    result = subprocess.run(
        ["stamped-l3-eval", "corpus", "list", "--corpus", str(CORPUS)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "w-md-001" in result.stdout
