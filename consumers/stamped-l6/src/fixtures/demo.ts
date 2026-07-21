import type {
  Alarm,
  ConnectionStatus,
  Prescription,
  TodaySignal,
} from "../lib/types";

export const DEMO_PLANT = {
  orgId: "org_demo",
  plantId: "plant_jaipur_01",
  plantName: "Jaipur Works",
};

export const connectionFixture: ConnectionStatus = {
  sse: "live",
  lastEventAt: "2026-07-21T10:15:00+05:30",
};

export const todaySignalsFixture: TodaySignal[] = [
  {
    id: "alarms",
    label: "Critical alarms",
    value: "2 open",
    tone: "critical",
    href: "/alarms",
    hint: "Ack before shift handoff",
  },
  {
    id: "rx",
    label: "Needs review",
    value: "₹2.14L / mo",
    tone: "warning",
    href: "/prescriptions",
    hint: "3 prescriptions",
  },
  {
    id: "savings",
    label: "Ops-confirmed (MTD)",
    value: "₹1.82L",
    tone: "good",
    href: "/reports",
    hint: "Not bill-verified",
  },
  {
    id: "deviation",
    label: "Vs baseline (7d)",
    value: "+6.2%",
    tone: "warning",
    href: "/evidence",
  },
  {
    id: "closure",
    label: "Closure rate (30d)",
    value: "64%",
    tone: "good",
    href: "/prescriptions",
  },
  {
    id: "stale",
    label: "Telemetry",
    value: "Fresh",
    tone: "neutral",
    href: "/evidence",
    hint: "Last sample 42s ago",
  },
];

export const alarmsFixture: Alarm[] = [
  {
    id: "alm_1001",
    plantId: DEMO_PLANT.plantId,
    assetId: "kiln_1",
    assetLabel: "Kiln 1",
    severity: "critical",
    state: "raised",
    summary: "Load 108% — 14% above design; MD coincidence risk",
    raisedAt: "2026-07-21T09:40:00+05:30",
    relatedPrescriptionId: "rx_9001",
    findingId: "fnd_4401",
  },
  {
    id: "alm_1002",
    plantId: DEMO_PLANT.plantId,
    assetId: "cm_1",
    assetLabel: "Cement Mill 1",
    severity: "warning",
    state: "acked",
    summary: "PF drifting toward penalty slab",
    raisedAt: "2026-07-21T08:10:00+05:30",
    ownerRole: "supervisor",
    relatedPrescriptionId: "rx_9002",
  },
  {
    id: "alm_1003",
    plantId: DEMO_PLANT.plantId,
    assetId: "comp_2",
    assetLabel: "Compressor 2",
    severity: "info",
    state: "cleared",
    summary: "Idle leak cleared after valve replace",
    raisedAt: "2026-07-20T16:00:00+05:30",
  },
];

export const prescriptionsFixture: Prescription[] = [
  {
    id: "rx_9001",
    plantId: DEMO_PLANT.plantId,
    title: "Stagger Kiln 1 co-start with Mill 2",
    why: "MD coincidence on incomer during 10–11 peak TOD",
    impactInrPerMonth: 84000,
    confidence: 0.86,
    lane: "needs_review",
    ownerRole: "supervisor",
    dueAt: "2026-07-22T18:00:00+05:30",
  },
  {
    id: "rx_9002",
    plantId: DEMO_PLANT.plantId,
    title: "APFC health check — Cement Mill 1",
    why: "PF slab breach projected this billing window",
    impactInrPerMonth: 38000,
    confidence: 0.91,
    lane: "active",
    ownerRole: "operator",
    dueAt: "2026-07-23T12:00:00+05:30",
  },
  {
    id: "rx_9003",
    plantId: DEMO_PLANT.plantId,
    title: "Compressor demand stagger",
    why: "Simultaneous load with packing line peaks",
    impactInrPerMonth: 26000,
    confidence: 0.78,
    lane: "verifying",
    ownerRole: "supervisor",
    dueAt: "2026-07-18T18:00:00+05:30",
    verificationStatus: "pending",
  },
  {
    id: "rx_9004",
    plantId: DEMO_PLANT.plantId,
    title: "Shift non-critical HVAC off peak",
    why: "TOD exposure on admin feeder",
    impactInrPerMonth: 12000,
    confidence: 0.7,
    lane: "closed",
    ownerRole: "energy_manager",
    dueAt: "2026-07-10T18:00:00+05:30",
    verificationStatus: "ops_confirmed",
    realisedInr: 11200,
    opportunityCost: {
      delayDays: 14,
      modeledInr: 5600,
      verificationStatus: "modeled",
    },
  },
];
