# Consumer repo README snapshots (L1–L6)

> **What it is:** Mirrored root `README.md` files from Stamped layer consumer repos, kept in the platform pack for cross-repo context.  
> **What it is not:** Canonical product docs — each consumer repo owns its README.  
> **Sync rule:** When a consumer README changes, re-copy it here and bump the snapshot date in that file’s banner.

---

## Index

| Layer | Repo name | Snapshot | Status |
|-------|-----------|----------|--------|
| **L1** | `connectors-edge` | [connectors-edge.md](./connectors-edge.md) | ✅ Mirrored |
| **L1** | `connectors-cloud` | [connectors-cloud.md](./connectors-cloud.md) | ✅ Mirrored |
| **L1** | `connectors-bill` | [connectors-bill.md](./connectors-bill.md) | ✅ Mirrored |
| **L2** | `universal-repositary` | [universal-repositary.md](./universal-repositary.md) | ✅ Mirrored (product: stamped-l2) |
| **L3** | `intelligence-core` | [intelligence-core.md](./intelligence-core.md) | ✅ Mirrored (product: stamped-l3-core) |
| **L3** | `intelligence-evals` | [intelligence-evals.md](./intelligence-evals.md) | ✅ Mirrored (product: stamped-l3-eval) |
| **L3** | `intelligence-rulepacks` | [intelligence-rulepacks.md](./intelligence-rulepacks.md) | ✅ Mirrored (product: stamped-l3-rulepacks) |
| **L4** | `knowledge-reasoning` | [knowledge-reasoning.md](./knowledge-reasoning.md) | ✅ Mirrored (product: stamped-l4) |
| **L5** | `closure-verification` | [closure-verification.md](./closure-verification.md) | ✅ Mirrored (product: stamped-l5) |
| **L6** | `stamped-l6` (planned) | [../stamped-l6/README.md](../stamped-l6/README.md) | 📋 Platform UI seed (not a live README snapshot) |

Related: [REPOS.md](../../REPOS.md) · [handoff/](../../handoff/) · scaffold code under [`../`](../) (reference only; not these snapshots).

## Re-sync one repo

```bash
# From stamped-external root, with sibling checkouts under ../
REPO=connectors-edge   # or connectors-cloud, intelligence-core, …
DATE=$(date -u +%Y-%m-%d)
{
  echo "<!-- SNAPSHOT: mirrored from ${REPO}/README.md on ${DATE}. Canonical README lives in the consumer repo — re-sync when that README changes. -->"
  echo ""
  echo "> **Snapshot** of [\`${REPO}\`](https://github.com/Vinayak-RZ/${REPO}) root README (copied ${DATE})."
  echo "> Canonical source: consumer repo \`README.md\`. Do not edit here for product truth — update the consumer repo, then re-copy."
  echo ""
  echo "---"
  echo ""
  cat "../${REPO}/README.md"
} > "consumers/readmes/${REPO}.md"
```

When L6 exists, add `<repo-name>.md` here and a row in the table above.
