export function statusLabel(status: string): string {
  if (status === "emitted") return "Emitted";
  if (status === "suppressed") return "Suppressed";
  if (status === "shadow_only") return "Shadow";
  if (status === "hypothesis") return "Hypothesis";
  return status;
}

export function deliveryLabel(delivery: string): string {
  if (delivery === "l4") return "L4 delivery";
  if (delivery === "lab_only") return "Lab-only";
  return delivery;
}

export function countByStatus(detections: { status: string }[]) {
  return {
    emitted: detections.filter((d) => d.status === "emitted").length,
    suppressed: detections.filter((d) => d.status === "suppressed").length,
    shadow_only: detections.filter((d) => d.status === "shadow_only").length,
    hypothesis: detections.filter((d) => d.status === "hypothesis").length,
  };
}

export function countByDelivery(detections: { delivery?: string }[]) {
  return {
    l4: detections.filter((d) => d.delivery === "l4").length,
    lab_only: detections.filter((d) => d.delivery === "lab_only").length,
  };
}

export function isAttributionScores(
  scores: Record<string, unknown> | null | undefined,
): boolean {
  if (!scores) return false;
  return (
    "ramp_kw" in scores ||
    "proximity" in scores ||
    "shadow_method" in scores ||
    "hops" in scores
  );
}
