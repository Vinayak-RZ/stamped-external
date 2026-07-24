# UI audit — https://trying.stamped.work

Audited: 2026-07-24T09:57:15.761Z

## Sidebar (home)
- Overview → /
- LiveReal-time → /live
- Ask Analyst → /analyst
- Alarms2 → /alarms
- AI Prescriptions → /prescriptions
- Live → /live
- Energy → /energy
- Tools → /tools

## Primary ops presence
- Alarms in nav: true
- Prescriptions in nav: true
- Evidence in nav: false

## Jam hypotheses
- Nav is denser than ADR-023 primary set (Today·Alarms·Rx·Evidence·Analyst·Reports)
- Evidence is reveal/reports-tier while Alarms+Rx sit under Operations — proof feels secondary
- Alarm and Rx pages both embed evidence snippets → concepts blur
- Overview mixes alarms + prescriptions + analytics signals in one board

## Route table
| Route | Status | H1 | Mix | Load ms |
|---|---|---|---|---|
| / | 200 | Overview | alarm+prescription co-present | 1017 |
| /alarms | 200 | Alarm console | alarm+prescription co-present; alarm+evidence co-present; rx+evidence co-present | 965 |
| /prescriptions | 200 | AI Prescriptions | alarm+prescription co-present | 870 |
| /evidence | 200 | Evidence index | alarm+prescription co-present; alarm+evidence co-present; rx+evidence co-present | 2233 |
| /live | 200 | Live | alarm+prescription co-present | 860 |
| /energy | 200 | Energy Analytics | alarm+prescription co-present | 1028 |
| /equipment | 200 | Machine Health | alarm+prescription co-present | 1096 |
| /plant-map | 200 | Plant Map | alarm+prescription co-present | 928 |
| /reports | 200 | Reports & ledger | alarm+prescription co-present; alarm+evidence co-present; rx+evidence co-present | 925 |
| /intensity | 200 | Intensity, TOD & CO₂ | alarm+prescription co-present | 985 |
| /analyst | 200 | Ask Analyst | alarm+prescription co-present | 883 |
| /tools | 200 | Tools | alarm+prescription co-present | 939 |
| /settings/admin | 200 | Organization admin | alarm+prescription co-present | 869 |

## Alarms deep dive
- Evidence links: [{"href":"/evidence/evd_4401","text":"Open evidence"}]
- Rx links: [{"href":"/prescriptions","text":"AI Prescriptions"},{"href":"/prescriptions/rx_9001","text":"Open prescription"}]
- Actions: Menu, Ask Analyst, Operations, Insights, Reports, Administration, Minimize, Kiln 1Criticalraised · Load 108% — 14% above design; MD coincidence risk in 10–11 TOD peak, Main incomerCriticalraised · Rolling 15-min MD at 4,680 kVA — 6.4% headroom to CMD, Admin HVACWarningacked · Off-peak schedule drift — still running into morning peak, Raw Mill 2Warningescalated · Idle draw 18% above night baseline for 47 minutes, Cement Mill 1Warningacked · PF 0.84 drifting toward penalty slab this billing window, Packing line 1Infosilenced · Short TOD overlap with packing surge — monitoring only, Acknowledge, Escalate, Silence

## Prescriptions deep dive
- Tabs: Needs review · Active · Verifying · Closed
- Evidence links: []

## Evidence deep dive
- Index cards: 4
- Detail: https://trying.stamped.work/evidence/evd_4401 — Kiln 1 · MD window
- Back-links: [{"href":"/alarms","text":"Alarms2"},{"href":"/prescriptions","text":"AI Prescriptions"},{"href":"/alarms/alm_1001","text":"← Back to alarm"}]