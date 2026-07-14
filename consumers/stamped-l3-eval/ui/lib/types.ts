export type DetectionStatus = "emitted" | "suppressed" | "shadow_only";
export type DetectorKind = "engine" | "rule" | "ml_shadow";

export interface Detection {
  detection_id: string;
  detector_kind: DetectorKind;
  rule_or_model_ref: string;
  category: string;
  status: DetectionStatus;
  finding: Record<string, unknown> | null;
  suppressions_checked: string[];
  scores: Record<string, unknown> | null;
  logs: string[];
}

export interface RunArtifact {
  schema_version: string;
  run_id: string;
  window_id: string;
  plant_id: string;
  started_at: string;
  core_version: string;
  rulepack_pins: { pack: string; version: string }[];
  inputs: Record<string, unknown>;
  detections: Detection[];
  timeline: { ts: string; step: string; detail: string }[];
  errors: string[];
}

export interface CorpusWindow {
  window_id: string;
  category: string;
  plant_id: string;
  asset: string;
  window: string;
  rulepack_ref: string;
}
