# stamped-l5 — Basic build plan (next agents)

> **Authority:** [stamped-l5-architecture-handoff.md](./stamped-l5-architecture-handoff.md) · [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · ADR-019/020/021/013  
> **Note:** Ops-first verification + EMS alarms. Bill path deferred. Expand commits in L5 workspace; do not contradict ADRs.

---

## §0 Metadata

| Field | Value |
| --- | --- |
| Objective | P0: workflow + EMS alarms + ops_clearance verify + calculated savings ledger |
| Non-goals | Bill-verified claims, IPMVP Option C gate, Temporal, Redis, L6 UI |
| Blockers | Finding 1.1.0 `ops_clearance` from L3; L2 measurement + ledger append (fixtures OK) |
| Estimated commits | **20–30** |

---

## §1 Workstreams

| ID | Owns |
| --- | --- |
| WS-A | Scaffold, CI, contracts pin |
| WS-B | Workflow + timers |
| WS-C | Alarm router + WhatsApp |
| WS-D | Ops clearance poller |
| WS-E | Ledger potential + ops_confirmed + opportunity_cost |
| WS-F | Hardening / tenancy / README |

---

## §2 Commit matrix (starter)

| # | Commit | Gate |
| --- | --- | --- |
| 1 | `chore: scaffold stamped-l5` | collect |
| 2 | `ci: ruff pytest contract-check` | CI |
| 3 | `feat(migrate): workflow alarms verification intents` | migrate |
| 4 | `feat(workflow): accept Rx + ops_clearance hard gate` | unit |
| 5 | `feat(alarms): raise ack escalate clear` | unit |
| 6 | `feat(notification): Meta + webhooks` | unit |
| 7 | `feat(verification): clearance predicate eval` | golden |
| 8 | `feat(verification): stabilize_window poller + regress` | integration |
| 9 | `feat(ledger): potential on accept` | unit |
| 10 | `feat(ledger): ops_confirmed realised on clear` | integration |
| 11 | `feat(ledger): opportunity_cost cron` | unit |
| 12 | `test(e2e): Rx → alarm → done → ops_verified → ledger` | e2e |
| 13 | `test: tenancy isolation` | pytest |
| 14 | `docs: README runbooks` | — |

---

## §3 Exit criteria (P0)

- [ ] Missing `ops_clearance` → bounce L4
- [ ] Alarm lifecycle works without dashboard
- [ ] Ops-clear sets Workflow VERIFIED + `ops_confirmed` ledger (not `verified` bill status)
- [ ] Regress reopens + compensating entry
- [ ] No UI copy claims DISCOM bill verification
- [ ] contract-check + e2e green
