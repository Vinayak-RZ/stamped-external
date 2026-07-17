# ADR-017: L4 adaptive retrieval and web-search trust tiers

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-17 |
| **Deciders** | Engineering (L4 architecture) |
| **Related** | [L4 spec](../technical/layers/L4-knowledge-and-reasoning.md) · [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-015](ADR-015-l3-dual-lane-lab-detections.md) · [handoff](../handoff/stamped-l4-architecture-handoff.md) |

---

## Context

L4 must ground prescriptions in a **large industrial practice corpus** (waste playbooks, BEE/PAT/SEC, equipment efficiency best practices, OEM manuals, plant SOPs) while staying **cost-efficient** and **audit-defensible**. Numbers and M&V methods must never come from free-form generation or untrusted web pages.

Three retrieval paradigms were evaluated for this corpus:

| Approach | Fit |
| --- | --- |
| Hybrid vector + BM25 + rerank | Best default for large semi-structured EE docs; cheap; metadata filters dominate quality |
| Knowledge-graph / GraphRAG | Strong multi-hop (asset ↔ waste ↔ standard ↔ remedy); higher index/ops cost |
| Vectorless structure-nav | Strong for long hierarchical PDFs (PAT manuals, tariff narrative); extra LLM nav cost |

Separately, product requires **web search ability** without poisoning the M&V trust model that previously assumed curated-only retrieval.

---

## Decision

1. **Adaptive hybrid RAG is the primary architecture.** A query classifier (deterministic from `finding.category` + doc-type hints; small LLM only if ambiguous) routes each lookup:
   - **Path H (default):** metadata filter → BM25 + dense RRF → cross-encoder rerank → CRAG-lite grade (one rewrite retry, then curated fallback)
   - **Path G:** light industrial knowledge graph (asset_type, waste_category, measure, standard_ref) over L2 graph + curated edges; use for multi-hop / relational queries
   - **Path V:** vectorless TOC/section navigation **inside a single `doc_id`** for long structured T1 manuals
   - **Path W:** allowlisted web search only when curated recall fails **and** the need is non-numeric advisory

2. **Trust tiers for evidence:**
   - **T1** curated Stamped / standards corpus
   - **T2** vendor OEM
   - **T3** tenant SOPs (injection-scanned; never overrides T1)
   - **T4** allowlisted web fetch — **never** sole source of ₹ / kWh / tCO₂e / M&V method; any prescription citing T4 requires **forced human approval**

3. **Dual retrieval backends** behind a `RetrievalBackend` interface:
   - Local: BGE-M3 + pgvector + BGE-reranker-v2-m3 (default)
   - Cloud: managed embeddings/vector optional for **shared** corpus only; tenant SOP embed/retrieve always local

4. **Web is a discovery channel:** fetched pages should be engineer-promoted into T2/T1 corpus when reusable — not a permanent runtime dependency for high-volume prescriptions.

5. **Tariff rate tables are not RAG:** structured into L2 `TariffContract`; RAG keeps narrative only. Impact calculator remains the sole ₹ source.

---

## Consequences

- `stamped-l4` implements Path H first; G/V/W are first-class architecture, not afterthoughts
- Eval harness must cover retrieval path selection, T4 forced-HITL, and cross-tier conflict (T1 beats T3/T4)
- Domain allowlist for Path W is config + CI-tested (BEE, CEA, MoP, DISCOM, major OEM)
- Conversational analyst may use Path W more freely; prescription path stays conservative
- Cost envelope assumes Path H dominance and rare Path W

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Pure vector RAG only | Misses multi-hop and long-manual structure; weaker audit path |
| Full GraphRAG as default index | Index/ops cost unjustified for most single-finding Rx |
| Vectorless-only fleet index | Immature ops; expensive LLM navigation at corpus scale |
| Open-web retrieval without trust tier | Poisons M&V defensibility; injection + citation risk |
| Curated-only forever (no web) | Blocks legitimate research / updated public EE guidance the product requires |
