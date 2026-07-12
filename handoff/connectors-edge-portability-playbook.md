# connectors-edge — Cloud + air-gap portability playbook

> **Authority:** [ADR-010](../decisions/ADR-010-deployment-profiles-and-portability.md) · [ADR-003](../decisions/ADR-003-connectors-edge-monorepo.md)  
> **Cross-repo:** [deployment-profiles.md](./deployment-profiles.md)

---

## 1. Current state (from README + audit)

**Repo:** `Vinayak-RZ/connectors-edge` (private — audit from handoff + ADR-003)

| Area | `cloud` mode today | Gap for `local*` |
|------|-------------------|------------------|
| edge-agent | MQTT uplink to Stamped EC2 Mosquitto | Needs `MQTT_BROKER_URL` → local compose broker |
| tag-mapping-api | AWS Fargate + SSM secrets | Colocate in compose; file/env secrets |
| tag-mapping-ui | S3 + CloudFront static | nginx-served build in compose (P1) |
| connectors-ingest | Lab: MQTT → local Timescale | **Valid in `local` mode**; deprecated for `cloud` |
| OTA | HTTPS pull from Stamped | Signed offline bundle (P1) |
| Templates | Git YAML in repo | Same — bundle in air-gap release |

### Audit appendix

```text
Audit checklist (connectors-edge)
├── README stated deployment model     → AWS-first; edge gateway cellular uplink
├── deploy/ directory inventory        → edge-agent Dockerfile; no profiles/ yet
├── AWS-specific dependencies          → tag-mapping-api: boto3/SSM (expected)
├── Hardcoded external URLs            → audit LLM/HuggingFace in tag-mapping-api
├── MQTT broker assumptions            → Stamped cloud broker host in env
├── Secrets management path            → SSM → must support file/.env
├── OTA/update mechanism               → HTTPS manifest → bundle P1
└── Existing compose vs prod gap       → connectors-ingest lab compose only
```

**Gap matrix:**

| Capability | `cloud` | `local` | Change required |
|------------|---------|---------|-----------------|
| edge-agent MQTT uplink | Yes | Partial (env only) | Document broker URL for local Mosquitto |
| tag-mapping-api | Yes (Fargate) | No | Add compose service + `LLM_BACKEND` |
| connectors-ingest lab path | Deprecated | **Yes** | Reclassify per ADR-010 |
| Zero egress edge-agent | N/A (uplink only) | Yes | No runtime pulls on edge |

---

## 2. Target: mode support matrix

| Package | `local` | `local-dashboard` | `cloud` |
|---------|---------|-------------------|---------|
| edge-agent | MQTT → compose broker | same | MQTT → EC2 Mosquitto |
| tag-mapping-api | compose optional | compose optional | Fargate |
| tag-mapping-ui | — (P1 compose) | via stamped-l6 or compose | S3/CloudFront |
| connectors-ingest | **enabled** | **enabled** | disabled after L2 E2E |

---

## 3. Architecture changes

1. **12-factor MQTT** — `MQTT_BROKER_URL`, `MQTT_TLS_CA`, `MQTT_CLIENT_CERT` from env; no hardcoded Stamped host.
2. **tag-mapping-api profile** — add `deploy/profiles/local.yml` service; `LLM_BACKEND=local|frontier|rules-only`.
3. **connectors-ingest** — gate with `STAMPED_DEPLOYMENT_MODE`: run in `local*`; document shutdown for `cloud`.
4. **OTA** — P0: env-driven manifest URL; P1: `OTA_BUNDLE_PATH` for signed tarball install.

---

## 4. File-by-file change list

| Path | Action | Detail |
|------|--------|--------|
| `deploy/profiles/local.yml` | **add** | edge-agent + optional tag-mapping-api (dev/lab) |
| `deploy/profiles/cloud.yml` | **add** | Reference Fargate task defs |
| `.env.example` | **modify** | `STAMPED_DEPLOYMENT_MODE`, `MQTT_BROKER_URL`, `LLM_BACKEND` |
| `packages/edge-agent/config/` | **modify** | Remove default cloud broker host |
| `packages/tag-mapping-api/` | **modify** | SSM optional; file secret fallback |
| `packages/connectors-ingest/README.md` | **modify** | Valid in `local` mode per ADR-010 |
| `docs/egress-inventory.md` | **add** | Per `docs/architecture/egress-inventory-template.md` in consumer repo |
| `scripts/egress-check.sh` | **add** | CI gate — no new external URLs |

---

## 5. New env vars and defaults per profile

| Variable | `local` default | `cloud` default |
|----------|-----------------|-----------------|
| `STAMPED_DEPLOYMENT_MODE` | `local` | `cloud` |
| `MQTT_BROKER_URL` | `mqtt://mosquitto:1883` | `mqtts://mosquitto.stamped.internal:8883` |
| `LLM_BACKEND` | `rules-only` (connectors) | `frontier` |
| `MAPPING_API_URL` | `http://tag-mapping-api:8080` | Fargate ALB URL |
| `OTA_MANIFEST_URL` | `file:///opt/stamped/ota/manifest.json` | HTTPS Stamped CDN |

---

## 6. deploy/profiles/ layout

```text
deploy/profiles/
├── local.yml          # edge-agent → local mosquitto (joint stack with cloud repo)
├── cloud.yml          # Fargate references only
└── ARCHITECTURE.md    # Link to stamped-l2 master compose
```

Edge joins the **full stack** compose in stamped-l2 repo for joint E2E; edge-only profile for field gateway testing.

---

## 7. Egress inventory (repo-specific)

| Call | Package | `local` edge-agent | Mitigation |
|------|---------|-------------------|------------|
| MQTT uplink | edge-agent | Allowed (internal broker) | Not internet |
| HTTPS OTA | edge-agent | Blocked P0 | Bundle install P1 |
| Frontier LLM | tag-mapping-api | Optional | `LLM_BACKEND=rules-only` |
| HuggingFace tokenizer | tag-mapping-api | **Block** | Vendor in image |

---

## 8. CI gates

- [ ] `scripts/egress-check.sh` — diff against committed inventory
- [ ] No new `boto3` imports in `packages/edge-agent` (Go — N/A)
- [ ] tag-mapping-api: `LLM_BACKEND=rules-only` smoke test in CI
- [ ] MQTT golden publish test against compose Mosquitto

---

## 9. OTA / update bundle process

**P0:** Document manual image retag + config push via SSH.

**P1 bundle contents:**

```text
stamped-edge-release-{version}.tar.gz
├── images/edge-agent-{digest}.tar
├── config/manifest.json (signed)
├── templates/verticals/*.yaml
└── checksums.sha256
```

Customer high-side ingest verifies signature → `docker load` → restart edge-agent.

---

## 10. Testing: E2E per profile

```bash
# local — joint stack (from stamped-l2 repo)
export STAMPED_DEPLOYMENT_MODE=local
docker compose -f deploy/profiles/local.yml up -d
# edge-agent publishes measurement → assert L2 hypertable row

# cloud — existing Fargate/EC2 path
export STAMPED_DEPLOYMENT_MODE=cloud
# Run existing integration tests against Stamped AWS
```

---

## 11. Phase breakdown

| Phase | Ships |
|-------|-------|
| **P0** | Env-driven MQTT broker; egress inventory; connectors-ingest `local` docs; compose profile sketch |
| **P1** | tag-mapping-api in compose; signed OTA bundle; UI nginx serve |
| **P2** | Hardware data diode topology doc |

---

## 12. Non-goals

- K3s/Helm on edge gateway
- Python runtime on edge device
- Inbound ports on plant network
- Separate edge codebase per mode
