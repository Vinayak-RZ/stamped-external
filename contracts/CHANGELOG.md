# Changelog — stamped-l1-contracts

## 0.8.0 — 2026-07-21

- `finding.json` **1.1.0**: additive `ops_clearance` + optional `alarm_hint` for L5 ops-first verification / EMS alarms
- `ledger-entry.json`: add `ops_confirmed` to `verification_status` (`verified` reserved for deferred bill path)
- `workflow-event.json`: add `alarm_raised|acked|cleared`, `ops_verified`, `ops_regressed`; actor `clearance_engine`
- Fixtures: `finding` with clearance, `workflow_event_ops_verified`, ledger `ops_confirmed`
- ADR-020 revised ops-first

## 0.7.0 — 2026-07-20

- Add `workflow-event.json` v1.0.0 — L5 → L6 workflow/notification stream (ADR-019)
- Extend `stamped-record-envelope.json` `record_type` with `workflow_event` (BACKWARD additive)
- `ledger-entry.json`: add optional `supersedes_entry_id`, `emission_factor_ref`; clarify `verification_status` (pending|verified|disputed|modeled) — no `superseded` status (corrections are new rows)
- `prescription.json`: document that `status` is intake-only; L5 verified/disputed live on WorkflowState
- Golden fixture `workflow_event.valid.json`
- Aligns with L5 architecture overhaul (ADR-019/020/021)

## 0.6.1 — 2026-07-14

- Docs: reconcile `Finding` examples in L3/L4/`02-technical-architecture` §5.2 to match `finding.json` field names (`baseline_value`/`actual_value`, required `plant_id`/`org_id`, top-level `engine` + `rule_or_model_ref`). Schema unchanged.

## 0.6.0 — 2026-07-13

- Add L3–L5 intelligence schemas: `finding.json`, `prescription.json`, `ledger-entry.json`, `capex-proposal.json`
- Extend `stamped-record-envelope.json` record_type enum: finding, prescription, ledger_entry, capex_proposal (BACKWARD additive)
- Add golden fixtures for Finding, Prescription, LedgerEntry (incl. opportunity_cost)
- ADR-012/013/014 accepted

## 0.5.0 — 2026-07-11

- Extend `event.json` enum: `bill_validated`, `bill_rejected`, `bill_published`, `document_received`, `ems_published`, `shift_calendar_uploaded`, `tariff_order_received` (BACKWARD additive)

## 0.4.0 — 2026-07-10

- Add `bill-line.json` for MQTT `bills` topic ingest
- Add required `seq` to `event.json` (layer-interfaces §2.2 dedupe)
- Require `batch_id` and `line_id` on `production-record.json` for dedupe stability

## 0.3.0 — 2026-07-10

- Add `stamped-record-envelope.json` — L1→L2 boundary wrapper (ADR-008, layer-interfaces.md)
- Document eight-repo topology: connectors-cloud (L1 cloud only); stamped-l2…l6 separate repos

## 0.2.0 — 2026-07-09

- Add `measurements/backfill` MQTT topic for late data beyond edge buffer horizon
- Add `tag_remapped?` event type for drift watch (L1 §4.5)
- Site config schema extended: `opcua`, `historian`, `rest_poller`, `dlms` connector blocks

## 0.1.0 — 2026-07-09

- Initial P0 schemas: measurement, event, production-record, site-config, mapping-config, tag-inventory, modbus-profile
- MQTT topic layout v1 in TOPICS.md (add `cmd/config` wake-up topic)
