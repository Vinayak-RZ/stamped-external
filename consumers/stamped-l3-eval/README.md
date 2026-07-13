# stamped-l3-eval

Golden corpus and rolling backtest CLI for L3 engine evaluation.

## Layout

```text
corpus/v0/windows.json     # synthetic eval windows
src/stamped_l3_eval/cli.py # CLI entry point
tests/test_cli.py          # pytest smoke tests
```

## Install

```bash
pip install -e ".[dev]"
```

## CLI

```bash
stamped-l3-eval corpus list
stamped-l3-eval backtest run
```

Both commands accept `--corpus` (defaults to `corpus/v0/windows.json`).

## Tests

```bash
pytest
```

## Related

- [ADR-012](../../decisions/ADR-012-l3-artifact-repo-topology.md)
- [L3 build order — Phase C](../../handoff/stamped-l3-build-order.md)
