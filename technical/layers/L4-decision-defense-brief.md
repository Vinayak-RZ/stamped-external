---
type: Decision Defense Brief
title: "L4 — Decision Defense Brief (Deterministic Workflows, RAG, and Agents)"
description: >-
  Rationale for every consequential L4 choice: deterministic LangChain workflows,
  bounded multi-hop RAG, model portability, safety, evaluation, pilot cuts, and
  evidence-driven upgrade triggers.
tags: [stamped-energy, l4, decisions, debate, tradeoffs, pedagogy]
timestamp: "2026-07-18T00:00:00Z"
status: Accepted pilot decisions — 1–2 plants, cheap-first, English only
---
# L4 Decision Defense Brief

> **Read this to challenge the architecture, not merely remember it.** Each decision names the selected option, alternatives, failure mode, pilot cut, and upgrade trigger.
>
> **Authority sources:**
> - Architecture SSOT: [`L4-knowledge-and-reasoning.md`](L4-knowledge-and-reasoning.md)
> - Upstream numeric architecture: [`L3-intelligence-core.md`](L3-intelligence-core.md)
> - Quality spine: [`../cross-cutting/04-evaluation-and-quality.md`](../cross-cutting/04-evaluation-and-quality.md)
> - Contracts: [`finding.json`](../../contracts/schemas/finding.json) · [`prescription.json`](../../contracts/schemas/prescription.json)
> - ADRs: [013](../../decisions/ADR-013-counterfactual-savings-ledger.md) · [015](../../decisions/ADR-015-l3-dual-lane-lab-detections.md) · [017](../../decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md)

---

## 0. How to use this document

| Goal | Section |
| --- | --- |
| Explain L4 in 60 seconds | §1 |
| Decide template vs LLM vs bounded analyst | §2 |
| Defend LangChain without an autonomous agent | §3.1 |
| Defend hybrid + two-hop RAG | §3.3–§3.6 |
| Defend external API + local model portability | §3.7–§3.9 |
| Defend the eval/observability stack | §3.10–§3.11 |
| Explain safety and human approval | §4 |
| Explain pilot cuts and upgrade triggers | §5 |
| Answer hostile architecture questions | §6–§7 |
| Know what not to claim | §8 |

**Honesty markers:** `[~]` is an estimate/target; `[!]` requires pilot validation.

---

## 1. One-sentence thesis

**L4 is a deterministic evidence-to-advice compiler with narrowly bounded LLM assistance: numbers and policy stay in code, knowledge comes from cited retrieval, and the model is used only where language or synthesis earns its cost.**

Expand it into six claims:

1. **L3 detects; L4 explains; L5 verifies.** Moving numeric truth into the LLM would destroy the layer boundary.
2. **A template is better than an agent when the answer shape is known.** Zero calls are cheaper and more reliable than a “small” call.
3. **RAG is a retrieval problem before it is a generation problem.** Corpus authority, metadata, and evaluation matter more than an elaborate orchestration diagram.
4. **Multi-hop is bounded evidence completion, not permission for open-ended research.**
5. **Local/API portability is proven by capability tests, not an OpenAI-compatible URL.**
6. **Production-grade means failure behavior, idempotency, observability, and rollback—not the number of AI frameworks installed.**

The trust boundary:

```text
L3 Finding + L2 evidence + deterministic impact + rules veto
                    │
                    ▼
        L4 templates / cited synthesis
                    │
                    ▼
          L5 approval and verification
```

---

## 2. Decision taxonomy — choose the least powerful tool

### 2.1 Five mechanisms

| Mechanism | Best at | Weak at | L4 use |
| --- | --- | --- | --- |
| Deterministic code | Exact numbers, routing, permissions, validation | Natural language | Workflow spine |
| Approved template | Repeated action cards | Novel synthesis | Lane A |
| Single structured LLM call | English composition over fixed evidence | Authority and arithmetic | Lane B / narrative |
| Bounded read-only tool loop | Variable analyst questions | Predictability/cost | Conversational analyst only |
| Human review | Ambiguity, risk, accountability | Throughput | Capex, safety, web, custom advice |

### 2.2 Selection rubric

Ask in order and stop at the first “yes”:

| # | Question | Use |
| --- | --- | --- |
| 1 | Must this be exact, auditable, or permission-enforcing? | Deterministic code |
| 2 | Does an approved template fully express the action? | Lane A, zero LLM |
| 3 | Is all evidence known and only English composition varies? | One structured call |
| 4 | Does the question require at most two evidence lookups? | Bounded two-hop synthesis |
| 5 | Is evidence insufficient, conflicting, risky, or novel? | Human review / abstain |
| 6 | Is someone asking the model to write OT or own ₹? | Reject |

### 2.3 Surface-specific autonomy

| Surface | Maximum autonomy | Why |
| --- | --- | --- |
| Prescription | Fixed workflow; 0–2 generation calls | Trust and repeatability |
| Analyst | Four model turns, six tools, two retrieval hops | Variable questions, read-only |
| Narrative | Template + optional one composition call | Ledger is structured |
| Web research | One allowlisted search pass | Freshness without open browsing |

---

## 3. Decision cards

### 3.1 LangChain primitives, deterministic application workflow

| | |
| --- | --- |
| **Decision** | Use LangChain models/retrievers/structured-output/Runnables, while plain application code owns a persisted state machine. Do not use `AgentExecutor` on the Prescription path. |
| **Why** | Provider and retrieval integrations are useful; model-owned routing is unnecessary for a fixed Finding→Prescription process. |
| **Rejected** | Free-form ReAct; LangGraph as default; custom model SDK wrappers only; multi-agent crews. |
| **Primary risk** | “LangChain” is misread as permission for an agent loop. |
| **Control** | Workflow states, transitions, budgets, and tool allowlist live outside prompts. |
| **Pilot cut** | PostgreSQL job/state table instead of graph checkpoint runtime. |
| **Upgrade trigger** | Multiple resumable model branches or long-lived approval loops make the explicit state machine harder to test than LangGraph. |

**Trade-off**

- **LangGraph:** excellent interrupts, graph replay, and checkpoint semantics; extra framework concepts and persistence behavior.
- **Plain state machine:** explicit, cheap, easy to unit-test; application owns recovery transitions.
- **Selected:** plain state machine because the production-critical route is fixed.

**Attack:** “If L4 is agentic, why remove the agent framework?”
**Answer:** Agentic capability is not measured by framework choice. The analyst still performs bounded tool use and synthesis. The money-bearing Prescription path is intentionally less autonomous.

### 3.2 Dual lane: templates before generation

| | |
| --- | --- |
| **Decision** | Lane A is an approved zero-call template path; Lane B is one structured synthesis call with one repair maximum. |
| **Why** | Known finding categories recur. A model call adds cost and variance without adding information. |
| **Rejected** | One frontier call for every Rx; one “smart” prompt covering every category; LLM-selected free-form actions. |
| **Failure feared** | A polished but unsupported maintenance instruction. |
| **Pilot cut** | Start with the categories L3 can produce and validate; unknown categories go to review. |
| **Upgrade trigger** | Real pilot findings repeatedly require evidence synthesis that templates cannot express. |

**Attack:** “Templates will sound robotic.”
**Answer:** Clear, accurate, repeated structure is a benefit on a plant floor. Language polish is not worth introducing uncertainty into a card whose purpose is action.

### 3.3 Hybrid sparse + dense retrieval

| | |
| --- | --- |
| **Decision** | Metadata filter → PostgreSQL FTS + pgvector → reciprocal-rank fusion. |
| **Why** | Sparse retrieval finds model numbers, standards, clauses, and engineering acronyms; dense retrieval finds paraphrases. RRF avoids comparing incompatible raw score scales. |
| **Rejected** | Dense-only vector RAG; BM25-only; dedicated vector DB at pilot scale. |
| **Failure feared** | Semantically similar but wrong OEM/standard/version chunk. |
| **Control** | Hard equipment/authority/version/tenant filters precede search. |
| **Pilot cut** | Exact scoring is acceptable while corpus size permits; HNSW only after measurement. |
| **Upgrade trigger** | Real corpus latency misses the SLO or retrieval eval identifies a modality-specific gap. |

**Attack:** “Modern embeddings make keyword search obsolete.”
**Answer:** Industrial documents contain exact identifiers, tariff names, standard clauses, units, and model numbers. Embeddings complement exact retrieval; they do not replace it.

### 3.4 Bounded two-hop synthesis without GraphRAG

| | |
| --- | --- |
| **Decision** | Permit at most two retrieval hops. Hop 1 finds the remedy/standard; hop 2 resolves one referenced OEM/standard/SOP section or L2 relationship. |
| **Why** | This captures the important compound cases without paying graph-extraction and entity-resolution costs. |
| **Rejected** | Single-hop only; unrestricted multi-hop agent; full Microsoft GraphRAG; recursive tree summaries. |
| **Failure feared** | Retrieval loops that accumulate loosely related context and cost. |
| **Control** | Validated entity/reference expansion and a hard hop ceiling. |
| **Pilot cut** | No separate knowledge-graph database; reuse L2 asset graph and corpus metadata. |
| **Upgrade trigger** | >20% of important queries need 3+ relationship traversals and the bounded approach fails a labelled slice. |

**Why this is better than plain single-hop:**
A compressor remedy may need both generic specific-power guidance and the exact OEM service limit. The second hop is valuable. A general-purpose agent planning five speculative searches is not.

### 3.5 Reranking is feature-flagged, not foundational

| | |
| --- | --- |
| **Decision** | Start without a cross-encoder reranker. |
| **Why** | Always-on reranking adds latency and cost; metadata + hybrid retrieval may already meet pilot quality. |
| **Rejected** | Mandatory managed reranker; self-hosted reranker service from day one. |
| **Failure feared** | Paying to reorder results that were already correct. |
| **Control** | Pool retrieval candidates and measure nDCG/claim citation before enabling. |
| **Upgrade trigger** | Relevant chunks regularly appear in top-20 but not top-5, and reranking materially fixes the locked cases. |

### 3.6 PostgreSQL FTS + pgvector, not another database

| | |
| --- | --- |
| **Decision** | L4 owns a PostgreSQL database/schema with workflow state, FTS, and pgvector. |
| **Why** | One backup, one access-control system, transactional corpus promotion, sufficient pilot scale. |
| **Rejected** | Pinecone/Qdrant/Weaviate plus Redis; placing L4 vectors inside the L2 application schema. |
| **Failure feared** | Operational surface exceeds the value of retrieval. |
| **Boundary** | L4 never uses L2 DB credentials; its Postgres is a distinct security principal. |
| **Upgrade trigger** | Measured filtered-search p95, index size, or availability needs exceed PostgreSQL. |

**Attack:** “A vector database is built for this.”
**Answer:** Capability is not the same as necessity. At pilot corpus size, Postgres gives hybrid search and governance without another service. Migrate after a measured bottleneck, not before.

### 3.7 External model API by default, local vLLM as a qualified option

| | |
| --- | --- |
| **Decision** | Use a small external structured-output model first; support a local vLLM endpoint through the same task capability contract. |
| **Why** | At expected low pilot volume, an external API is the lower-operations default; a local GPU becomes preferable only if measured utilisation, quality, availability, and total cost support it. |
| **Rejected** | Buy GPU before load data; API-only lock-in; Ollama as assumed production server. |
| **Failure feared** | “OpenAI compatible” hides differences in JSON Schema, tool choice, limits, and quality. |
| **Control** | Every deployment passes frozen per-task evals and declares capabilities. |
| **Upgrade trigger** | Qualified local quality/SLO plus measured TCO beats API including utilisation and operations. |

**Attack:** “Local is always cheaper.”
**Answer:** A GPU has fixed cost, power, patching, monitoring, spare capacity, and availability requirements. Local is cheaper only at measured sustained utilisation with a model that passes the same quality gate.

**Data boundary:** External API use is allowed only after classifying and redacting the payload, approving provider retention/no-training terms, documenting processing region/sub-processors, and testing the boundary. T3 SOP text is local by default unless its data owner explicitly approves external processing.

### 3.8 Thin application adapter, not a model gateway yet

| | |
| --- | --- |
| **Decision** | Application-owned model contract implemented with LangChain adapters. |
| **Why** | One application and a few deployments do not justify another proxy/service. |
| **Rejected** | LiteLLM gateway as mandatory foundation; direct provider-specific calls throughout the code. |
| **Failure feared** | Silent model fallback changes quality while looking operationally successful. |
| **Control** | Explicit model qualification and actual provider/model provenance. |
| **Upgrade trigger** | Multiple applications need central keys, budgets, aliases, and routing policy. |

### 3.9 Strict structured output plus deterministic semantic validation

| | |
| --- | --- |
| **Decision** | Bind a JSON Schema/Pydantic model, then separately validate domain semantics and citations. |
| **Why** | Constrained decoding protects shape; it does not protect truth. |
| **Rejected** | Regex parse/free-form JSON; treating schema validity as correctness. |
| **Failure feared** | Valid JSON containing an invented ₹ amount or unsafe step. |
| **Control** | Numeric diff, evidence resolution, template policy, owner map, M&V and veto checks. |
| **Upgrade trigger** | None—semantic validation is permanent. |

### 3.10 OpenTelemetry + Phoenix + pytest

| | |
| --- | --- |
| **Decision** | Use OTel for neutral instrumentation, Phoenix for traces/datasets/experiments, pytest for hard gates. |
| **Why** | Covers pilot observability and evaluation with one optional service and standard telemetry. |
| **Rejected** | Mandatory Langfuse + Phoenix + DeepEval + RAGAS + LangSmith; proprietary tracing as the only record. |
| **Failure feared** | More time reconciling eval tools than improving cases. |
| **Control** | Add individual evaluator libraries only for a missing diagnostic. |
| **Upgrade trigger** | Prompt lifecycle, annotation workflow, or team-scale experiment management materially exceeds Phoenix. |

**Why not LangSmith by default?** It is convenient with LangChain, but the architecture should not couple production telemetry to one commercial control plane. OTel preserves the option.

### 3.11 Deterministic gates before LLM judges

| | |
| --- | --- |
| **Decision** | Hard checks run on 100% of outputs; calibrated judges sample residual language quality. |
| **Why** | Numeric equality, citation resolution, isolation, and step budgets are facts—do not ask another model. |
| **Rejected** | One “quality score” from an LLM judge; judge every production response. |
| **Failure feared** | Judge bias masks deterministic violations while adding cost. |
| **Control** | Claim-level human-labelled calibration; high-risk cases always human. |
| **Upgrade trigger** | Higher sample rate only after calibrated judge reliability and operational need. |

### 3.12 Curated web research, never silent web RAG

| | |
| --- | --- |
| **Decision** | Web is an explicit T4 route with allowlist, snapshot, provenance, one-pass budget, and approval for Rx use. |
| **Why** | Current public guidance matters, but web content is mutable and untrusted. |
| **Rejected** | Automatic web fallback inside every RAG query; open crawl ingestion. |
| **Failure feared** | Prompt injection or outdated advice silently outranks reviewed internal knowledge. |
| **Control** | Internal retrieval first unless freshness is explicit; web evidence labelled separately. |
| **Upgrade trigger** | Frequent proven freshness misses plus demonstrated review capacity. |

### 3.13 No persistent semantic memory in the pilot

| | |
| --- | --- |
| **Decision** | Store session messages/summaries for UX; rebuild factual answers from tools. |
| **Why** | Persistent “memory” can preserve stale facts, cross tenant boundaries, and complicate deletion. |
| **Rejected** | Vector memory of every conversation; model-decided long-term memory. |
| **Failure feared** | An old operator comment becomes invisible product truth. |
| **Control** | Explicit saved notes with author/time/source if persistence is needed. |
| **Upgrade trigger** | User research proves continuity needs cannot be met by current plant data and explicit notes. |

---

## 4. Safety decisions that are not tradeable

### 4.1 Advisory-only autonomy

L4 never writes OT or sends a command. This is not a pilot shortcut; it is the product safety boundary.

**Why:** energy advice interacts with production, electrical protection, maintenance safety, and capex. A language model is not a control system or authorised approver.

**Rejected:** RL control, model-written PLC logic, automatic setpoint optimisation, WhatsApp “done” triggering actuation.

### 4.2 Deterministic numbers

Every ₹, kWh, kVA, and tCO₂e value must resolve to a typed tool result. A model may select which supplied value belongs in a field only under a fixed schema; it may not derive the value in prose.

**Important correction to the basic scaffold:** comparing an L4 impact to the L3 estimate within 1% is not enough. The authoritative value must come from the pinned calculator/tariff inputs; L3's estimate is evidence, not L4's money truth.

### 4.3 Final rules veto

If `check_rule_violation` is unavailable, L4 fails closed. If it vetoes, L4 may not “reason around” it. Revision is allowed only if a different approved template/parameter set addresses the stated violation.

### 4.4 Human checkpoints

Human review is mandatory for capex, production interruption, safety relevance, T4 evidence, low confidence, and custom advice. L5 owns the approval state because L5 owns closure and accountability.

### 4.5 Prompt injection is contained, not declared solved

OWASP and NIST do not offer a foolproof detector. The design assumes malicious instructions can appear in SOPs, PDFs, web pages, and tool results. Security comes from permissions and workflow outside the model.

---

## 5. Pilot minimum versus fleet extensions

### 5.1 What is deliberately small

| Pilot choice | Why it is sufficient |
| --- | --- |
| Modular monolith | Two plants do not justify distributed services |
| PostgreSQL job table | Fixed workflows; transactional and inspectable |
| Hybrid retrieval | Covers exact + semantic document lookup |
| Two retrieval hops | Covers one relationship/reference completion |
| One model provider + local qualification | Cheap without architectural lock-in |
| Phoenix + pytest | Enough traces, datasets, and hard gates |
| English only | Removes multilingual model/eval uncertainty |
| Manual corpus approval | Small corpus; high trust |
| Manual category graduation | Safer than global launch |

### 5.2 What was removed from the basic architecture

- LangGraph as required runtime
- CRAG grading/rewrite loops on every query
- LLM query router for known finding categories
- mandatory cross-encoder reranker
- GraphRAG and vectorless production paths
- self-hosted BGE embedding/rerank services
- three overlapping eval/trace platforms
- online judge on every Prescription
- automatic web fallback
- Hindi/Hinglish
- persistent agent memory
- multi-agent decomposition

These are not banned forever. They require evidence.

### 5.3 Upgrade principle

**No component is promoted because it is fashionable.** Promotion requires:

1. a labelled failing slice;
2. a candidate implementation;
3. improved quality on the locked slice;
4. no regression on safety/isolation;
5. acceptable latency/cost/operations;
6. recorded decision and rollback path.

---

## 6. Architecture attack / response cards

### Attack 1: “A deterministic workflow is not an agentic layer.”

**Response:** L4 has bounded tool use, retrieval, synthesis, analyst decomposition, and model portability. It is agentic where variability exists and deterministic where trust demands it. Calling a fixed business process an autonomous agent would be branding, not engineering.

### Attack 2: “Use one frontier model—it will simplify everything.”

**Response:** It simplifies the demo while making cost, arithmetic, permissions, and replay probabilistic. The model does not have fresher plant telemetry than L2 or more authoritative tariff math than code.

### Attack 3: “GraphRAG is more accurate.”

**Response:** More accurate for which labelled Stamped query slice? GraphRAG helps global/relationship-heavy synthesis but has extraction, entity-resolution, indexing, and update costs. We retain multi-hop value using metadata + the existing L2 asset graph and add GraphRAG only if that fails.

### Attack 4: “Why not vectorless RAG for manuals?”

**Response:** Tree navigation can help long documents, but it introduces model-dependent retrieval latency and another indexing model. Section-aware chunks plus page/section metadata are cheaper and evaluable. Vectorless becomes an experiment if long-manual misses persist.

### Attack 5: “Reranking always improves RAG.”

**Response:** Often, not universally, and it charges on every query. If the right chunk is already top-5 after filters/RRF, reranking adds no value. Enable it against measured misses.

### Attack 6: “Local models protect us from API costs.”

**Response:** They exchange variable API spend for fixed GPU, operations, model serving, monitoring, and availability. The adapter supports local inference; procurement waits for quality and TCO evidence.

### Attack 7: “Use automatic model fallback for reliability.”

**Response:** Operational success with a lower-quality fallback can silently create product failure. Fallback is safe only between deployments qualified for the same task and recorded in provenance.

### Attack 8: “An LLM judge can automate QA.”

**Response:** It can provide a noisy regression signal. It cannot replace exact numeric/citation/security checks or energy-engineer review. Judges have order, verbosity, and self-preference biases.

### Attack 9: “Web search makes the corpus unnecessary.”

**Response:** A mutable page is not an audit record. Internal corpus snapshots provide reviewed, versioned, reproducible evidence. Web is for freshness/discovery and is separately labelled.

### Attack 10: “Why not ship every finding to maximise savings?”

**Response:** Supervisor attention is the scarce resource. Precision and closure dominate raw alert volume. L4 caps open work and blocks unsupported candidates.

---

## 7. Steelman Q&A drills

### Q1. Why LangChain instead of plain provider SDKs?

**Answer:** It gives consistent model/retriever/Runnable integrations and observability hooks. Business workflow semantics still belong to application code, preventing framework lock-in from becoming architecture lock-in.

### Q2. Why not LangGraph now if it may be needed later?

**Answer:** A future migration rewires typed transition functions; it does not rewrite domain logic. Paying graph complexity today does not reduce uncertainty about whether the future workflow will actually need it.

### Q3. How is two-hop retrieval deterministic?

**Answer:** The category evidence recipe defines eligible expansions. Hop-1 entities must resolve to known corpus metadata or L2 graph IDs. Hop 2 runs once. No model can invent a third tool path.

### Q4. How can one model adapter support API and local models?

**Answer:** The adapter contract is task/capability based. Compatibility is earned by schema, quality, cost, and latency evals—not assumed from protocol compatibility.

### Q5. What happens if the model is unavailable?

**Answer:** Lane A continues with zero calls. Lane B queues review. Analyst abstains. No numerical detection or L5 verification is lost because those live outside the model.

### Q6. What happens if retrieval is wrong?

**Answer:** Citations, authority/version filters, claim validation, and abstention limit the result. Retrieval evals identify whether the miss was filtering, sparse, dense, fusion, chunking, or corpus coverage.

### Q7. Why store workflow state in L4 Postgres rather than L2?

**Answer:** L2 is the universal data repository accessed by API. L4 operational state has different ownership, retention, and failure semantics. Sharing credentials would violate the boundary.

### Q8. What makes the Prescription reproducible?

**Answer:** Finding IDs/versions, tool result references, calculator/tariff versions, template/workflow versions, prompt/schema/model IDs, corpus snapshot, retrieved chunk IDs, and approval record.

### Q9. What prevents duplicate prescriptions?

**Answer:** Input-derived run/idempotency keys, unique constraints, root-cause/template dedupe, and an idempotent L5 emit key. We design for at-least-once attempts, not pretend remote calls are exactly once.

### Q10. How do you know the architecture is cheap?

**Answer:** Hard per-surface call/token/currency ceilings, zero-call default, no GPU, no extra database, and measured telemetry. The ₹ budget is a target; actual spend is reported, not assumed.

### Q11. Why is Phoenix enough?

**Answer:** It covers traces, datasets, experiments, evaluations, and human labels while OTel preserves portability. Additional tools need a missing workflow, not feature-list envy.

### Q12. Why no Hindi now?

**Answer:** The pilot requirement is English. Multilingual generation changes embeddings, corpus, fonts/rendering, evaluation, and safety review. Shipping it without demand would dilute quality.

### Q13. Can the analyst issue a Prescription?

**Answer:** No. It may prepare a cited candidate that re-enters the normal Prescription workflow. Conversation is not a bypass around intake, impact, veto, or approval.

### Q14. Is a web result ever authoritative?

**Answer:** Only after source-specific review and corpus promotion. Runtime T4 web evidence remains externally labelled and cannot own impact or M&V truth.

### Q15. What is the first upgrade likely to be?

**Answer:** A reranker or more templates—whichever the first labelled pilot failures support. Not GraphRAG by default.

---

## 8. Do not overclaim

Do not claim before representative evaluation:

- local inference is cheaper than an API;
- one provider can replace another without quality change;
- strict JSON makes content correct;
- temperature 0 is deterministic;
- prompt injection is prevented;
- hybrid retrieval is “90% accurate” without a labelled set;
- GraphRAG/vectorless would improve Stamped;
- the two-hop strategy covers every multi-hop question;
- ₹1,500/month is an actual bill rather than a budget;
- 60 synthetic cases represent live plant behavior;
- accepted prescriptions prove realised savings;
- the analyst is an engineering authority;
- a model recommendation is safe because it cites a document;
- a fallback model preserves quality;
- an LLM judge score is ground truth.

**Customer-facing truth:** verified savings come from L5 M&V and the bill, not from L4 prose or estimated opportunity.

---

## 9. Known dependencies and unresolved decisions

### Blocking integration dependencies

1. L3 durable outbox consumer interface with cursor/ack or webhook idempotency.
2. L3 `check_rule_violation` HTTP contract.
3. L2 typed query APIs for telemetry, baseline, graph, and role map.
4. Deterministic impact calculator ownership and versioned tariff inputs.
5. L5 idempotent Prescription intake and approval states.

### Open pilot questions

- Which external model passes the frozen English Prescription/analyst eval cheapest?
- Does pgvector exact search meet corpus latency without ANN?
- Do actual pilot queries need reranking?
- What percentage of findings require Lane B?
- Which documents are permitted in external model context?
- What engineer review capacity exists for T4 web evidence?

None of these require changing the safety boundary.

---

## 10. Source-backed reasoning

| Decision area | Primary reference | What it supports |
| --- | --- | --- |
| LangChain primitives | https://docs.langchain.com/oss/python/langchain/retrieval | Retrieval/components, not business-policy delegation |
| LangGraph later | https://docs.langchain.com/oss/python/langgraph/persistence | Durable graph/checkpoint trade-offs |
| Hybrid Postgres | https://github.com/pgvector/pgvector | Vector + PostgreSQL FTS/RRF composition |
| Local serving | https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/ | Production-like local API path |
| Ollama limitations | https://docs.ollama.com/api/openai-compatibility | Partial compatibility; qualify behavior |
| OTel GenAI | https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/ | Portable model usage/latency attributes |
| Phoenix | https://arize.com/docs/phoenix | Traces, datasets, experiments, evals |
| RAG security | https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html | Provenance, isolation, poisoned content controls |
| Prompt injection | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | Defense in depth; no foolproof prompt |
| GenAI risk | https://doi.org/10.6028/NIST.AI.600-1 | Indirect injection and risk controls |
| OT boundary | https://csrc.nist.gov/pubs/sp/800/82/r3/final | Safety/reliability-specific OT posture |
| M&V | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf | Savings require baseline and adjustments |
| BEE corpus | https://beeindia.gov.in/en/pat-downloads | Authoritative Indian industrial EE source |

---

## 11. Final defense

The architecture is intentionally asymmetric:

```text
Maximum determinism where a wrong answer costs trust or money
Maximum model flexibility only where the result is reversible and cited
```

That is why:

- prescriptions are compiled, not improvised;
- multi-hop is bounded, not autonomous;
- retrieval is hybrid, not graph-heavy;
- model serving is portable, not falsely interchangeable;
- eval starts with hard gates, not judge vibes;
- the pilot is small without being fragile;
- every advanced component has a measurable reason to exist before it is added.
