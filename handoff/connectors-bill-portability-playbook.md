# connectors-bill — Cloud + air-gap portability playbook

> **Authority:** [ADR-010](../decisions/ADR-010-deployment-profiles-and-portability.md)  
> **Spec:** [connectors-bill-spec.md](./connectors-bill-spec.md)

---

## 1. Current state (from README + audit)

**Repo:** `Vinayak-RZ/connectors-bill` (private — audit from handoff spec)

| Area | `cloud` mode today | Gap for `local*` |
|------|-------------------|------------------|
| PDF storage | S3 presigned URLs | MinIO or local volume |
| extract | Cloud API / Docling | Containerized; `LLM_BACKEND` switch |
| web UI | CloudFront + Next.js | nginx-served in compose |
| MQTT publish | Stamped EC2 broker | compose `mosquitto` |
| validate Postgres | Cloud RDS | Container Postgres |
| publish | MQTT QoS 1 | Same transport |

### Audit appendix

```text
Audit checklist (connectors-bill)
├── README stated deployment model     → AWS S3 + Fargate + CloudFront
├── deploy/ directory inventory        → TBD in bill repo
├── AWS-specific dependencies          → boto3 S3, presigned URLs
├── Hardcoded external URLs            → audit extract LLM/OCR endpoints
├── MQTT broker assumptions            → env MQTT_BROKER_URL
├── Secrets management path            → SSM
├── OTA/update mechanism               → CI/CD
└── Existing compose vs prod gap       → likely none
```

**Gap matrix:**

| Capability | `cloud` | `local` | Change required |
|------------|---------|---------|-----------------|
| Bill upload UI | Yes | No | Compose web service |
| S3 PDF store | Yes | No | `STORAGE_BACKEND=local|minio` |
| OCR/extract | Yes | Partial | Local container + LLM policy |
| MQTT publish | Yes | Partial | Local broker URL |
| Zero egress | No | Target | Egress CI + rules-only path |

---

## 2. Target: mode support matrix

| Package | `local` | `local-dashboard` | `cloud` |
|---------|---------|-------------------|---------|
| web (PWA) | compose nginx | compose or stamped-l6 embed | CloudFront |
| api | compose | compose | Fargate |
| extract | compose | compose | Fargate |
| publish | compose | compose | Fargate |
| storage | MinIO / volume | same | S3 |

---

## 3. Architecture changes

1. **Storage adapter** — `STORAGE_BACKEND=s3|minio|local`; uniform presigned-URL interface internally.
2. **LLM policy** — `LLM_BACKEND=local|frontier|rules-only`; rules-only must pass recompute gate on templates.
3. **MQTT** — same topic family; broker from env.
4. **No S3 SDK in `local` path** — adapter selects MinIO (S3-compatible) or filesystem.

---

## 4. File-by-file change list

| Path | Action | Detail |
|------|--------|--------|
| `deploy/profiles/local.yml` | **add** | api + web + extract + publish + minio |
| `deploy/profiles/cloud.yml` | **add** | ECS + S3 reference |
| `packages/ingest/storage/` | **add/modify** | Storage adapter interface |
| `packages/extract/` | **modify** | `LLM_BACKEND` switch |
| `packages/web/` | **modify** | API URL from env |
| `.env.example` | **add** | All storage + LLM vars |
| `docs/egress-inventory.md` | **add** | Repo inventory |
| `scripts/egress-check.sh` | **add** | CI gate |

---

## 5. New env vars and defaults per profile

| Variable | `local` default | `cloud` default |
|----------|-----------------|-----------------|
| `STAMPED_DEPLOYMENT_MODE` | `local` | `cloud` |
| `STORAGE_BACKEND` | `minio` | `s3` |
| `MINIO_ENDPOINT` | `http://minio:9000` | — |
| `S3_BUCKET` | `stamped-bills` | `stamped-bills-prod` |
| `MQTT_BROKER_URL` | `mqtt://mosquitto:1883` | `mqtts://...` |
| `LLM_BACKEND` | `rules-only` | `frontier` |
| `DATABASE_URL` | compose Postgres | RDS |

---

## 6. deploy/profiles/ layout

```text
deploy/profiles/
├── local.yml       # bill services + minio
├── cloud.yml       # ECS + S3
└── ARCHITECTURE.md
```

Bill profile fragment merges into stamped-l2 master `local.yml`.

---

## 7. Egress inventory (repo-specific)

| Call | Package | `local` | Mitigation |
|------|---------|---------|------------|
| S3/MinIO | api | Internal MinIO | compose network |
| Frontier LLM | extract | Optional | `LLM_BACKEND=rules-only` |
| Docling model download | extract | **Block at runtime** | Bake models in image |
| MQTT publish | publish | Internal broker | compose mosquitto |
| WhatsApp (P2) | — | N/A P0 | Out of scope |

---

## 8. CI gates

- [ ] Dedupe hash matches golden for `bill_line.valid.json`
- [ ] `scripts/egress-check.sh`
- [ ] Recompute gate passes with `LLM_BACKEND=rules-only` on fixture bills
- [ ] Compose E2E: upload PDF → MQTT → cloud ingest

---

## 9. OTA / update bundle process

**`local`:** Bundle includes DISCOM template updates (`packages/templates/`), extract model weights, and container images. Templates are semver-versioned artifacts per production engineering spec.

---

## 10. Testing: E2E per profile

```bash
# local
docker compose -f deploy/profiles/local.yml up -d
curl -F file=@fixtures/sample_bill.pdf http://localhost:3001/api/upload
# Assert MQTT message on bills topic; cloud ingest receives

# cloud — existing pilot path
```

---

## 11. Phase breakdown

| Phase | Ships |
|-------|-------|
| **P0** | Storage adapter; MinIO compose; MQTT env; egress CI |
| **P1** | `LLM_BACKEND=local` with vLLM sidecar |
| **P2** | stamped-l6 deep-link for bill status |

---

## 12. Non-goals

- L2 table writes from bill repo
- MQTT subscribe in bill repo
- Customer-facing full L6 dashboard (owned by stamped-l6)
