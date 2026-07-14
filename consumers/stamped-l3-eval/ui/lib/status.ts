export function statusLabel(status: string): string {
  if (status === "emitted") return "Emitted";
  if (status === "suppressed") return "Suppressed";
  if (status === "shadow_only") return "Shadow";
  return status;
}

export function countByStatus(detections: { status: string }[]) {
  return {
    emitted: detections.filter((d) => d.status === "emitted").length,
    suppressed: detections.filter((d) => d.status === "suppressed").length,
    shadow_only: detections.filter((d) => d.status === "shadow_only").length,
  };
}
