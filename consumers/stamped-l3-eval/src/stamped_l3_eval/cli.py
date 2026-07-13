"""stamped-l3-eval CLI — corpus list + backtest run (skeleton)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
