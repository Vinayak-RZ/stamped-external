# stamped-l3-rulepacks

Semver YAML rulepack artifacts for L3 incomer engines (MD overlap, PF slab, TOD exposure).

## Layout

```text
incomer/1.0.0/
├── manifest.yaml          # semver + rules index
└── rules/
    ├── md_overlap.yaml
    ├── pf_slab.yaml
    └── tod_exposure.yaml
fixtures/
└── golden_md_spike.json   # input window + expected finding fields
tests/
└── test_golden_replay.py  # golden replay CI gate
```

## Platform pin

Mount platform contracts via submodule:

```bash
git submodule add https://github.com/vinayak-rz/stamped-external.git external
cd external && git checkout v2026.07.12
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Golden replay validates `expected_finding.category` against the MD spike fixture. Full engine replay lands in `stamped-l3-core` (B9 rulepack loader + B4 MD engine).

## Related

- [ADR-012](../../decisions/ADR-012-l3-artifact-repo-topology.md)
- [L3 build order](../../handoff/stamped-l3-build-order.md)
