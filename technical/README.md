---
type: Directory Guide
title: "Stamped Energy — Technical Context Pack"
description: "Self-contained technical knowledge pack for the Stamped product repo: master document, improved product and technical architectures, six deeply-researched layer specs (L1–L6), and two cross-cutting engineering docs."
tags: [stamped-energy, technical]
timestamp: "2026-07-09T00:00:00Z"
---
# Stamped Energy — Technical Context Pack

This folder is a **portable, self-contained context pack** for Stamped Energy engineering. In this repo it lives at `external/technical/` (Connectors / L1).

It carries everything an engineer (or coding agent) needs to start building the product:

1. **What Stamped is** — the master company/product document.
2. **How it is architected** — product architecture (what customers buy, mapped to layers) and the detailed technical architecture (the engineering spec, with savings math, layer contracts, and resolved technology decisions).
3. **How each layer is built** — one deeply-researched spec per architecture layer (L1–L6), each covering the researched landscape, recommended approach, testing/evaluation, and build phasing.
4. **How it is engineered for production** — cross-cutting specs on production-grade system design and on evaluation/testing/quality.

It deliberately contains **no market, ICP, or GTM research** beyond what the master document itself carries.

## Reading order

| # | Document | Read it for |
| --- | --- | --- |
| 1 | [00-stamped-master-document.md](00-stamped-master-document.md) | What Stamped is: positioning, product vision, capabilities, outcomes, ICP summary, revenue model |
| 2 | [01-product-architecture.md](01-product-architecture.md) | Product definition: 10 capability modules, UX surfaces, integration paths, competitor learnings, module→layer map |
| 3 | [02-technical-architecture.md](02-technical-architecture.md) | The engineering spec: L0–L6 stack, savings math for 15–20%, layer contracts, resolved decisions, build phases |
| 4 | [cross-cutting/03-production-engineering.md](cross-cutting/03-production-engineering.md) | Streaming backbone, reliability patterns, edge, tenancy, observability, deployment |
| 5 | [cross-cutting/04-evaluation-and-quality.md](cross-cutting/04-evaluation-and-quality.md) | The quality spine: testing pyramid, data-quality gates, ML/LLM evals, CI gates, shadow mode |
| 6+ | `layers/` (below) | Per-layer deep dives, in build order |

## The seven-layer stack and its specs

```
L0  Plant systems (customer-owned, read-only)      — not Stamped-built
L1  Connect & normalise                            → layers/L1-connect-and-normalise.md
L2  Universal Repository (six stores)              → layers/L2-universal-repository.md
L3  Intelligence core (models + rules)             → layers/L3-intelligence-core.md
L4  Knowledge & reasoning (agentic RAG)            → layers/L4-knowledge-and-reasoning.md
L5  Closure & verification (workflow, WhatsApp, M&V) → layers/L5-closure-and-verification.md
L6  Experience & integration (dashboard, API)      → layers/L6-experience-and-integration.md
```

| Layer spec | Scope |
| --- | --- |
| [L1 — Connect & normalise](layers/L1-connect-and-normalise.md) | Protocol landscape (OPC UA, Modbus, MQTT, DLMS/COSEM, BACnet…), realistic connector inventory and build order, edge gateway, DISCOM bill/tariff ingest, canonical normalisation schema |
| [L2 — Universal Repository](layers/L2-universal-repository.md) | Time-series DB choice, energy graph modelling, feature/baseline stores, commercial context (Indian tariff structures), append-only M&V ledger, tenancy and retention |
| [L3 — Intelligence core](layers/L3-intelligence-core.md) | Model families per engine (baselines, anomaly, MD forecasting, attribution), rules/physics packs, per-plant calibration, cold start, and the per-engine evaluation protocol |
| [L3 — Decision defense brief](layers/L3-decision-defense-brief.md) | Debate-ready synthesis: rules vs ML vs LLM vs foundation models, engine attack/response cards, ADR-012/014 topology & shadowing, eval gates, Zerowatt counters |
| [L3 — Attribution explainability](layers/L3-attribution-explainability.md) | Co-start/graph ranking of-record; quality grade; why not SHAP/NILM; dual-lane + ADR-016 shadows |
| [L4 — Knowledge & reasoning](layers/L4-knowledge-and-reasoning.md) | Architecture SSOT: dual-lane agent, adaptive hybrid RAG (H/G/V/W), T4 web trust, dual local/cloud retrieval, Langfuse+Phoenix+DeepEval — [ADR-017](../decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md) · [handoff](../handoff/stamped-l4-architecture-handoff.md) |
| [L5 — Closure & verification](layers/L5-closure-and-verification.md) | **SSOT** — workflow, WhatsApp, IPMVP M&V, bill reconciliation, L2 ledger append, evidence, P0–P3 cost (ADR-019/020/021) |
| [L6 — Experience & integration](layers/L6-experience-and-integration.md) | Dashboard stack, prescription queue UX, report/export generation, REST API + webhooks, tiered "connect to any system" integration menu |

## Cross-cutting engineering specs

| Spec | Scope |
| --- | --- |
| [03 — Production engineering](cross-cutting/03-production-engineering.md) | Postgres outbox backbone at pilot scale (upgrade: Redpanda), event-driven patterns, edge resilience, modular monolith + satellites, observability SLOs, deployment and security |
| [04 — Evaluation & quality](cross-cutting/04-evaluation-and-quality.md) | Testing pyramid, data-quality gates, ML per-engine eval protocol, LLM/agent eval harness, shadow mode, CI gates, ledger feedback loop |

## Conventions used across the pack

- **Honesty markers:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before relying on it.
- **Layer contracts:** the four canonical schemas (`Measurement`, `Finding`, `Prescription`, `LedgerEntry`) are defined in [02-technical-architecture.md §5](02-technical-architecture.md) and referenced by every layer spec.
- **Build phases:** P0 (weeks 1–8, MD/bill wedge) → P1 (months 3–6, full OT depth) → P2 (months 6–12, fleet + dispatch) → P3 (depth). Every spec phases its recommendations against these.
- **Citations:** each researched doc ends with a numbered `# Citations` section of sources.
- **Implementation decisions:** living ADRs in [`../decisions/`](../decisions/) (repo split, edge packaging, MQTT, tag mapping, compliance). Canonical schemas draft in [`../contracts/`](../contracts/).
- **Compliance:** Indian regulations register in [`../compliance/`](../compliance/).

## The one-line thesis to keep in mind while building

> 15–20% verified bill reduction is engineered as the **sum of closed prescriptions across six waste categories**, multiplied by **closure rate**, defended by **bill-verified M&V** — not produced by any single model. Detection is necessary; closure and verification are the product.
