# Stamped product repositories

Consumer repos mount this platform pack as a git submodule at `external/`.

| Repo | GitHub | Layer | Submodule | Platform pin (target) |
|------|--------|-------|-----------|----------------------|
| connectors-edge | `Vinayak-RZ/connectors-edge` | L1 plant | `external/` | `v2026.07.12` |
| connectors-cloud | `Vinayak-RZ/connectors-cloud` | L1 cloud | `external/` | `v2026.07.12` |
| connectors-bill | `Vinayak-RZ/connectors-bill` | L1 bill | `external/` | `v2026.07.12` |
| stamped-l2 | `Vinayak-RZ/universal-repositary` | L2 | `external/` | `v2026.07.12` |
| stamped-l3-core | `Vinayak-RZ/stamped-l3-core` (planned) | L3 engine | `external/` | — |
| stamped-l3-rulepacks | `Vinayak-RZ/stamped-l3-rulepacks` (planned) | L3 artifacts | `external/` | — |
| stamped-l3-eval | `Vinayak-RZ/stamped-l3-eval` (planned) | L3 eval | `external/` | — |
| stamped-l4 | `Vinayak-RZ/stamped-l4` (planned) | L4 | `external/` | — |
| stamped-l5 | `Vinayak-RZ/stamped-l5` (planned) | L5 | `external/` | — |
| stamped-l6 | `Vinayak-RZ/stamped-l6` (planned) | L6 | `external/` | — |

**L4 handoff:** [handoff/stamped-l4-architecture-handoff.md](handoff/stamped-l4-architecture-handoff.md) · [ADR-017](decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md)

**Platform repo:** `vinayak-rz/stamped-external` — see [SUBMODULE.md](SUBMODULE.md)

Update this table when a consumer bumps its pin.
