# L1 canonical contracts

Shared schemas and MQTT topic conventions for all L1 publishers (edge agent, bill ingest) and L2 consumers.

**Package name (when published):** `stamped-l1-contracts`  
**Canonical source:** this directory in **[stamped-platform](https://github.com/vinayak-rz/stamped-external)** ([ADR-011](../decisions/ADR-011-stamped-platform-submodule-distribution.md))

| Artifact | Status |
| --- | --- |
| JSON Schemas (`schemas/*.json`) | **Implemented** — v0.1.0 |
| Golden fixtures (`fixtures/*.json`) | **Implemented** — valid payloads + dedupe vectors |
| [TOPICS.md](TOPICS.md) | Draft topic layout |
| [CHANGELOG.md](CHANGELOG.md) | Starts at 0.1.0 |

**CI:** run [../scripts/contract-check.sh](../scripts/contract-check.sh) from consumer repo (path: `external/scripts/contract-check.sh`).

**Bootstrap:** [../handoff/README.md](../handoff/README.md). See [ADR-001](../decisions/ADR-001-l1-repo-split-and-boundaries.md).
