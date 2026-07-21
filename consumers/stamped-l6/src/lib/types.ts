/** Shared L6 reference types — mirror contracts, do not invent fields. */

export type Role =
  | "operator"
  | "supervisor"
  | "plant_head"
  | "energy_manager"
  | "sustainability"
  | "cfo"
  | "admin";

export type AlarmState =
  | "raised"
  | "acked"
  | "escalated"
  | "silenced"
  | "cleared";

export type AlarmSeverity = "critical" | "warning" | "info";

export type VerificationStatus =
  | "pending"
  | "ops_confirmed"
  | "modeled"
  | "disputed"
  | "verified";

export type PrescriptionLane =
  | "needs_review"
  | "active"
  | "verifying"
  | "closed";

export interface Alarm {
  id: string;
  plantId: string;
  assetId: string;
  assetLabel: string;
  severity: AlarmSeverity;
  state: AlarmState;
  summary: string;
  raisedAt: string;
  ownerRole?: Role;
  relatedPrescriptionId?: string;
  findingId?: string;
}

export interface Prescription {
  id: string;
  plantId: string;
  title: string;
  why: string;
  impactInrPerMonth: number;
  confidence: number;
  lane: PrescriptionLane;
  ownerRole: Role;
  dueAt: string;
  verificationStatus?: VerificationStatus;
  realisedInr?: number;
  opportunityCost?: {
    delayDays: number;
    modeledInr: number;
    verificationStatus: "modeled";
  };
}

export interface TodaySignal {
  id: string;
  label: string;
  value: string;
  hint?: string;
  tone: "neutral" | "critical" | "good" | "warning";
  href: string;
}

export type FocusEntityType =
  | "alarm"
  | "prescription"
  | "asset"
  | "ledger_entry";

export interface AnalystContextEnvelope {
  orgId: string;
  plantId: string;
  userId: string;
  role: Role;
  routeId: string;
  screenTitle: string;
  focusEntity?: { type: FocusEntityType; id: string };
  visibleSummary: string[];
  timeRange?: { from: string; to: string };
  excludeKeys?: string[];
}

export interface ConnectionStatus {
  sse: "live" | "reconnecting" | "offline";
  lastEventAt?: string;
}

export type NavKey =
  | "today"
  | "alarms"
  | "prescriptions"
  | "evidence"
  | "analyst"
  | "reports"
  | "energy"
  | "equipment"
  | "intensity"
  | "integrations"
  | "admin";
