# ADR-018: L4 pilot execution — knowledge-reasoning consumer (P0–P2)

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-19 |
| **Deciders** | Engineering (L4 consumer implementation) |
| **Related** | [L4 SSOT](../technical/layers/L4-knowledge-and-reasoning.md) · [ADR-017](ADR-017-l4-adaptive-retrieval-and-web-trust.md) · [ADR-015](ADR-015-l3-dual-lane-lab-detections.md) · [handoff](../handoff/stamped-l4-architecture-handoff.md) · Consumer repo [Vinayak-RZ/knowledge-reasoning](https://github.com/Vinayak-RZ/knowledge-reasoning) |

---

## Context

The L4 architecture SSOT (July 2026) describes a cheap-first, durable prescription compiler with optional analyst, Path W, and Phoenix. The consumer repo **`knowledge-reasoning`** (Python package `stamped_l4`) implemented P0–P2 against that SSOT and recorded several execution decisions that either **pull upgrade triggers early** or **clarify ownership / deferrals**.

This ADR promotes those decisions into the platform pack so other layers (especially L6) and future L4 work share one authority. Where this ADR and the pre-ADR SSOT text conflict, **this ADR + the updated SSOT sections win**.

---

## Decision

### 1. Consumer identity

| Item | Value |
| --- | --- |
| GitHub repo | `knowledge-reasoning` |
| Python package | `stamped_l4` |
| Platform scaffold | `consumers/stamped-l4/` (Lane A reference only) |
| Live consumer README (mirrored) | [`consumers/knowledge-reasoning/README.md`](../consumers/knowledge-reasoning/README.md) |

Single-package layout under `src/stamped_l4/` (not a multi-package monorepo).

### 2. LangGraph as orchestration shell from P0 (early pull of §17 trigger)

Use **LangGraph `StateGraph`** as the workflow substrate for:

- Lane A — linear graph, **zero LLM nodes**;
- Lane B — retrieve → impact → draft/repair → claims → verify → veto → emit;
- Analyst — budgeted **ReAct** (`agent` ↔ `tools` → finalize).

Business logic remains plain functions. Application code still owns routing, budgets, veto, and emit. Checkpointers: MemorySaver in unit tests; SqliteSaver / PostgresSaver for durable resume.

**Rationale:** Lane B and analyst resume were expected immediately after Lane A; a throwaway custom FSM would impose migration tax. Safety/budget rules from the SSOT still apply.

### 3. Lane B generation budget (SSOT-aligned)

Normal **1**, hard max **2** structured generation calls via application-owned `generate_structured()` / `GenerationBudget`. Mock model in CI; real OpenAI-compatible provider only when `L4_MODEL_PROVIDER=openai_compat` and base URL / API key / model name are set.

### 4. Path H pilot shape (bounded hop-2)

Pilot Path H (in-process seed corpus for CI / early plant):

```text
metadata filter → FTS5 sparse + hash-dense → RRF → hop-2 same-doc neighbors (≤3) → top_k
```

Hop-2 is **not** a second LLM query rewrite. It expands the top fused hit’s `doc_id` siblings so playbook context is not a single orphaned paragraph. Cross-encoder rerank, CRAG rewrite, Path G, and Path V remain architecture targets per ADR-017 but are **not** required for P0–P2 exit.

### 5. Analyst memory and budgets (P2)

| Memory | Rule |
| --- | --- |
| Session transcript | Durable in L4 Postgres |
| Rolling summary | Compact UX context |
| Explicit saved notes | Plant + user scoped; never auto-embed chat as corpus |
| Product truth | Rebuilt each turn from Path H / L2 tools / Path W |

| Budget knob | Default | Hard max |
| --- | ---: | ---: |
| Model turns / cycle | 6 | 8 |
| Tool calls / cycle | 8 | 12 |
| Retrieval hops (tool calls to Path H) | 2 | 2 |
| Path W passes / cycle | 1 | 1 |
| Wall clock | 45 s | 60 s |

(Earlier SSOT “four turns / six tools” is superseded for pilot by these defaults.)

### 6. UI ownership — L6 only

L4 exposes **HTTP APIs only** (plus optional eng-only `/dev/chat` behind a flag). Plant dashboard, prescription queue, and operator chat UX are **L6**. L4 does not ship a branded product UI.

### 7. Path W in P2; Path G deferred

Path W (allowlisted BEE / CEA / MoP / DISCOM / OEM) ships for the analyst in P2, labelled **T4**, one-pass cap. Fixture transport in CI; `httpx` when `L4_PATH_W_LIVE=1` or `L4_PATH_W_TRANSPORT=httpx`. Path G GraphRAG remains post-P2 / trigger-gated.

### 8. Observability — Phoenix optional in P2

pytest gates are the CI bar. OpenTelemetry spans + optional Arize Phoenix compose profile (`L4_PHOENIX_*`). Phoenix unavailable must not block prescriptions. Langfuse is **not** required for the pilot consumer.

### 9. Live L2 / L3 / L5 HTTP deferred to post-P2 deploy

P0–P2 use fixture / VCR backends. Live clients remain stubs until cutover after deploy. Documented in the consumer at `docs/cutover-live-http.md`.

### 10. Language — English only through P2 (far future for Hindi)

Hindi / Hinglish are **not** Core/P1/P2 milestones. Ignore older handoff maturity rows that placed Hindi under Core.

### 11. Sustainability narrative deferred to P3

Not implemented in P0–P2.

### 12. Runtime topology for pilot

In-repo `docker-compose`: `api` + `worker` + dedicated L4 Postgres; optional Phoenix via compose profile `obs`. Durable jobs use lease claim (`FOR UPDATE SKIP LOCKED`) + fencing tokens.

### 13. Eval bar

≥60 expert-style cases in CI (mock model, no live upstreams): schema, numeric integrity, citations, budgets, adversarial unsafe rate 0, tenant isolation.

---

## Consequences

- Platform SSOT and handoff must reflect LangGraph-as-pilot-substrate, L6 UI ownership, English-through-P2, and post-P2 live HTTP.
- L6 integrators consume chat/jobs APIs from `knowledge-reasoning`; they do not expect an L4 SPA.
- ADR-017 Path G/V/rerank remain valid architecture; pilot implements Path H (+ hop-2) and Path W first.
- Consumer `DECISIONS.md` D1–D8 / P1-D* / P2-D* remain the execution log; this ADR is the platform summary.

---

## Alternatives considered

| Alternative | Why rejected for pilot |
| --- | --- |
| Custom FSM until “LangGraph trigger” | Migration tax into Lane B/analyst within weeks |
| Product chat UI in L4 | Violates L6 ownership; duplicates dashboard work |
| Live upstream HTTP in P1 | Deploy/credentials not ready; fixtures keep CI deterministic |
| Hindi in Core band | Product priority is English for 1–2 pilot plants |
| Always-on Phoenix | Optional; pytest gates are the merge bar |

---

## References

- Consumer completion: `knowledge-reasoning` `PHASE_P2_COMPLETION.md`
- Mirrored README: [`consumers/knowledge-reasoning/README.md`](../consumers/knowledge-reasoning/README.md)
