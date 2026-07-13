# ADR-014 promotion decision — TimesFM shadow eval

| Field | Value |
| --- | --- |
| **Date** | 2026-07-13 |
| **Decision** | **Do not promote** — remain shadow-only |
| **Evidence** | P2 skeleton run; timesfm optional dep not installed in CI |

## Gate results (P2 skeleton)

| Gate | Result |
| --- | --- |
| Beats seasonal-naive on pinball loss | Not run — no pilot corpus wired |
| Beats LightGBM | Not run |
| FP regression on golden corpus | Not run |
| Batch latency SLO | N/A |

## Action

Continue with LightGBM primary for MD exceedance. Re-run `stamped-l3-eval backtest run --shadow timesfm` when `timesfm>=2.0.2` installed and ≥3 plant windows available.
