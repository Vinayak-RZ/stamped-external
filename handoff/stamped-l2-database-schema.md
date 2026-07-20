# stamped-l2 — Database schema (P0)

> **Authority:** Research spec [L2-universal-repository.md](../technical/layers/L2-universal-repository.md) §4.1–4.8  
> **Migrations:** `packages/migrate/sql/` — apply in order  
> **Database:** `stamped_l2` on RDS PostgreSQL 16 + TimescaleDB extension

---

## 1. Schema overview

| Schema | Purpose | P0 tables |
| --- | --- | --- |
| `ingest` | L1 idempotency | `l1_processed_inbox`, `l1_ingest_audit` |
| `telemetry` | Time-series | `measurement`, `event` (optional P0), caggs |
| `graph` | Energy topology | `asset`, `asset_edge` (edges Phase B) |
| `commercial` | Tariffs, bills, production | `tariff_version`, `bill`, `bill_line`, `shift_calendar`, `emission_factor`, `production_record` |
| `features` | Derived metrics | Deferred P1 — read from caggs in P0 |
| `baselines` | M&V reference | `baseline` |
| `ledger` | Verified savings | `mv_ledger` |

**Bootstrap:**

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS ingest;
CREATE SCHEMA IF NOT EXISTS telemetry;
CREATE SCHEMA IF NOT EXISTS graph;
CREATE SCHEMA IF NOT EXISTS commercial;
CREATE SCHEMA IF NOT EXISTS features;
CREATE SCHEMA IF NOT EXISTS baselines;
CREATE SCHEMA IF NOT EXISTS ledger;
```

---

## 2. Ingest schema

```sql
CREATE TABLE ingest.l1_processed_inbox (
  dedupe_key     text PRIMARY KEY,
  envelope_id    uuid NOT NULL,
  record_type    text NOT NULL
    CHECK (record_type IN ('measurement','event','production_record','bill_line')),
  org_id         text NOT NULL,
  plant_id       text NOT NULL,
  ingested_at    timestamptz NOT NULL,
  processed_at   timestamptz NOT NULL DEFAULT now(),
  correlation_id uuid
);

CREATE INDEX l1_inbox_org_plant_idx ON ingest.l1_processed_inbox (org_id, plant_id, processed_at DESC);

CREATE TABLE ingest.l1_ingest_audit (
  audit_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dedupe_key     text,
  record_type    text,
  org_id         text,
  plant_id       text,
  status         text NOT NULL CHECK (status IN ('accepted','duplicate','rejected')),
  error_code     text,
  received_at    timestamptz NOT NULL DEFAULT now()
);
```

---

## 3. Telemetry schema

### 3.1 measurement hypertable

```sql
CREATE TABLE telemetry.measurement (
  org_id        text        NOT NULL,
  plant_id      text        NOT NULL,
  asset_id      text        NOT NULL,
  metric        text        NOT NULL,
  ts            timestamptz NOT NULL,
  value         double precision NOT NULL,
  quality       smallint    NOT NULL DEFAULT 0,  -- 0 good | 1 estimated | 2 bad
  source_system text,
  source_tag    text,
  dedupe_key    text        UNIQUE
);

SELECT create_hypertable('telemetry.measurement', by_range('ts', INTERVAL '7 days'));

CREATE INDEX measurement_org_plant_asset_metric_ts_idx
  ON telemetry.measurement (org_id, plant_id, asset_id, metric, ts DESC);
```

**P0 columnstore:** Defer compression policies until >7 days hot data; enable in Phase B per L2 spec §4.1.

### 3.2 Continuous aggregate (15 min)

```sql
CREATE MATERIALIZED VIEW telemetry.agg_15min
WITH (timescaledb.continuous) AS
SELECT
  org_id,
  plant_id,
  asset_id,
  metric,
  time_bucket(INTERVAL '15 minutes', ts) AS bucket,
  avg(value) FILTER (WHERE quality = 0) AS avg_value,
  min(value) FILTER (WHERE quality = 0) AS min_value,
  max(value) FILTER (WHERE quality = 0) AS max_value,
  count(*) AS point_count
FROM telemetry.measurement
GROUP BY org_id, plant_id, asset_id, metric, bucket;

SELECT add_continuous_aggregate_policy('telemetry.agg_15min',
  start_offset => INTERVAL '3 days',
  end_offset   => INTERVAL '15 minutes',
  schedule_interval => INTERVAL '15 minutes');
```

### 3.3 event hypertable (Phase B / when SCADA live)

```sql
CREATE TABLE telemetry.event (
  org_id      text NOT NULL,
  plant_id    text NOT NULL,
  asset_id    text,
  event_type  text NOT NULL,
  ts          timestamptz NOT NULL,
  payload     jsonb NOT NULL DEFAULT '{}'::jsonb,
  dedupe_key  text UNIQUE
);

SELECT create_hypertable('telemetry.event', by_range('ts', INTERVAL '7 days'));
```

---

## 4. Graph schema

```sql
CREATE TABLE graph.asset (
  org_id      text NOT NULL,
  plant_id    text NOT NULL,
  asset_id    text PRIMARY KEY,
  parent_id   text REFERENCES graph.asset(asset_id),
  level       text NOT NULL CHECK (level IN ('plant','system','equipment','measurement_point')),
  asset_class text,
  name        text NOT NULL,
  owner_role  text,
  attrs       jsonb DEFAULT '{}'::jsonb,
  valid_from  timestamptz NOT NULL DEFAULT now(),
  valid_to    timestamptz
);

CREATE TABLE graph.asset_edge (
  org_id     text NOT NULL,
  from_asset text NOT NULL REFERENCES graph.asset(asset_id),
  to_asset   text NOT NULL REFERENCES graph.asset(asset_id),
  edge_type  text NOT NULL CHECK (edge_type IN
    ('feeds','drives','shares_electrical_bus','starts_with','thermal_coupling')),
  attrs      jsonb DEFAULT '{}'::jsonb,
  PRIMARY KEY (from_asset, to_asset, edge_type)
);

CREATE INDEX asset_edge_to_idx ON graph.asset_edge (to_asset);
```

**P0 seed:** One incomer `measurement_point` per pilot plant — required for measurement FK or nullable FK with incomer default.

---

## 5. Commercial schema

```sql
CREATE TABLE commercial.tariff_version (
  org_id                    text NOT NULL,
  plant_id                  text NOT NULL,
  tariff_version_id         text PRIMARY KEY,
  discom                    text NOT NULL,
  category                  text NOT NULL,
  valid_from                date NOT NULL,
  valid_to                  date,
  cmd_kva                   numeric NOT NULL,
  billing_demand_floor_pct  numeric NOT NULL DEFAULT 75,
  demand_charge_inr_per_kva numeric,
  energy_charge_inr_per_kwh numeric,
  kvah_billing              boolean DEFAULT false,
  source_doc                text
);

CREATE TABLE commercial.tod_window (
  tariff_version_id text REFERENCES commercial.tariff_version(tariff_version_id),
  season            text,
  window_start      time,
  window_end        time,
  kind              text CHECK (kind IN ('peak_surcharge','offpeak_rebate','normal')),
  pct_of_energy_charge numeric
);

CREATE TABLE commercial.pf_slab (
  tariff_version_id text REFERENCES commercial.tariff_version(tariff_version_id),
  pf_from numeric,
  pf_to   numeric,
  effect  text CHECK (effect IN ('surcharge','incentive')),
  pct_per_step numeric,
  step    numeric
);

CREATE TABLE commercial.bill (
  org_id     text NOT NULL,
  plant_id   text NOT NULL,
  bill_id    text NOT NULL,
  bill_month date NOT NULL,
  discom     text,
  PRIMARY KEY (org_id, plant_id, bill_id)
);

CREATE TABLE commercial.bill_line (
  org_id      text NOT NULL,
  plant_id    text NOT NULL,
  bill_id     text NOT NULL REFERENCES commercial.bill(org_id, plant_id, bill_id),
  bill_month  date NOT NULL,
  line_type   text NOT NULL,
  qty         numeric,
  rate        numeric,
  amount_inr  numeric NOT NULL,
  dedupe_key  text PRIMARY KEY,
  validated   boolean NOT NULL DEFAULT true,
  ingested_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE commercial.shift_calendar (
  org_id    text NOT NULL,
  plant_id  text NOT NULL,
  shift_id  text NOT NULL,
  name      text NOT NULL,
  start_time time NOT NULL,
  end_time   time NOT NULL,
  PRIMARY KEY (org_id, plant_id, shift_id)
);

CREATE TABLE commercial.emission_factor (
  factor_id           text PRIMARY KEY,
  source              text NOT NULL,
  version             text NOT NULL,
  fiscal_year         text NOT NULL,
  factor_tco2_per_mwh numeric NOT NULL,
  published_on        date NOT NULL
);

CREATE TABLE commercial.production_record (
  org_id       text NOT NULL,
  plant_id     text NOT NULL,
  batch_id     text NOT NULL,
  sku          text,
  qty          numeric,
  uom          text,
  window_start timestamptz NOT NULL,
  window_end   timestamptz,
  source       text,
  dedupe_key   text PRIMARY KEY,
  PRIMARY KEY (org_id, plant_id, batch_id)
);
```

**P0 tariff seed:** JVVNL Rajasthan HT industrial template — see migration `seed_jvvnl_tariff.sql`.

---

## 6. Baselines schema

```sql
CREATE TABLE baselines.baseline (
  org_id                  text NOT NULL,
  plant_id                text NOT NULL,
  baseline_id             text PRIMARY KEY,
  scope                   jsonb NOT NULL,
  model_type              text NOT NULL,
  model_params            jsonb NOT NULL,
  feature_set_version     text,
  training_window_start   timestamptz NOT NULL,
  training_window_end     timestamptz NOT NULL,
  version                 int NOT NULL DEFAULT 1,
  supersedes              text REFERENCES baselines.baseline(baseline_id),
  status                  text NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','active','locked','retired')),
  locked_at               timestamptz,
  locked_by_prescription  text,
  created_at              timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION baselines.reject_locked_baseline_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.status = 'locked' AND NEW.status IS DISTINCT FROM 'retired' THEN
    RAISE EXCEPTION 'baseline % is locked', OLD.baseline_id;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER baseline_lock_guard
  BEFORE UPDATE ON baselines.baseline
  FOR EACH ROW EXECUTE FUNCTION baselines.reject_locked_baseline_update();
```

---

## 7. Ledger schema

```sql
CREATE TABLE ledger.mv_ledger (
  org_id              text NOT NULL,
  plant_id            text NOT NULL,
  entry_id            uuid NOT NULL DEFAULT gen_random_uuid(),
  seq                 bigint NOT NULL,
  prescription_id     text NOT NULL,
  entry_type          text NOT NULL DEFAULT 'realised_savings'
    CHECK (entry_type IN ('realised_savings','potential_savings','opportunity_cost')),
  period_start        timestamptz NOT NULL,
  period_end          timestamptz NOT NULL,
  mv_method           text NOT NULL,
  baseline_id         text NOT NULL REFERENCES baselines.baseline(baseline_id),
  potential_kwh       numeric,
  realised_kwh        numeric,
  potential_inr       numeric,
  realised_inr        numeric,
  avoided_tco2e       numeric,
  verification_status text NOT NULL DEFAULT 'pending'
    CHECK (verification_status IN ('pending','verified','disputed','modeled')),
  -- Corrections are new rows; do not mutate prior verification_status to 'superseded'
  supersedes_entry_id uuid,
  emission_factor_ref text,
  modeled_reason      text,
  delay_days          integer,
  bill_line_refs      text[],
  dedupe_key          text NOT NULL UNIQUE,
  reason_code         text,
  created_at          timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (org_id, entry_id)
);

REVOKE UPDATE, DELETE, TRUNCATE ON ledger.mv_ledger FROM PUBLIC;

CREATE OR REPLACE FUNCTION ledger.reject_ledger_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'ledger.mv_ledger is append-only';
END;
$$;

CREATE TRIGGER ledger_immutable
  BEFORE UPDATE OR DELETE ON ledger.mv_ledger
  FOR EACH ROW EXECUTE FUNCTION ledger.reject_ledger_mutation();
```

Hash chain columns (`prev_entry_hash`, `entry_hash`) — defer to P1.

---

## 8. Row-level security (RLS)

**Pattern:** shared schema + `org_id` column + RLS as defence-in-depth.

```sql
-- App sets per transaction:
-- SET LOCAL app.current_org = 'org_acme';

CREATE POLICY tenant_isolation ON telemetry.measurement
  USING (org_id = current_setting('app.current_org', true));

ALTER TABLE telemetry.measurement ENABLE ROW LEVEL SECURITY;
-- Repeat for ALL tenant-scoped tables
```

**CI requirement:** For every table with `org_id`, automated test queries as org A must return zero org B rows. New table without RLS policy → CI fail.

**Roles:**

| Role | Privileges |
| --- | --- |
| `l2_migrate` | DDL, owned by migrate job |
| `l2_app` | INSERT/SELECT on L2 schemas; no UPDATE/DELETE on ledger |
| `l2_readonly` | SELECT only (analytics/debug) |

---

## 9. Retention policies (P0)

| Dataset | Retention | Mechanism |
| --- | --- | --- |
| Raw measurement | 13 months | Timescale retention policy (Phase B) |
| agg_15min | 36 months | Cagg retention |
| bill_line, tariff | Life of customer + 8 years | No auto-drop |
| Locked baselines | Never delete | — |
| mv_ledger | Forever (append-only) | Partition by month P1 |

P0: configure retention after first pilot month of data ingested.

---

## 10. Indexes checklist

- All tenant tables: leading index column `org_id`
- Hypertables: `(org_id, plant_id, asset_id, metric, ts DESC)`
- `commercial.bill_line`: `(org_id, plant_id, bill_month)`
- `graph.asset`: `(org_id, plant_id)`

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial P0 schema map for stamped-l2 handoff |
