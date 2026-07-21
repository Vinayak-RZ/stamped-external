import type { AnalystContextEnvelope } from "./types";

/**
 * Build the user-visible context chips for Mode A analyst.
 * Strips excluded keys; never includes secrets.
 */
export function visibleContextChips(
  envelope: AnalystContextEnvelope,
): string[] {
  const excluded = new Set(envelope.excludeKeys ?? []);
  const chips: string[] = [];

  const candidates: Array<{ key: string; value: string }> = [
    { key: "screen", value: envelope.screenTitle },
    { key: "route", value: envelope.routeId },
    {
      key: "focus",
      value: envelope.focusEntity
        ? `${envelope.focusEntity.type}:${envelope.focusEntity.id}`
        : "",
    },
    ...(envelope.timeRange
      ? [
          {
            key: "range",
            value: `${envelope.timeRange.from} → ${envelope.timeRange.to}`,
          },
        ]
      : []),
    ...envelope.visibleSummary.map((s, i) => ({
      key: `summary:${i}`,
      value: s,
    })),
  ];

  for (const c of candidates) {
    if (!c.value || excluded.has(c.key)) continue;
    chips.push(c.value);
  }
  return chips;
}

/** Reject cross-tenant focus entities at the BFF boundary. */
export function assertTenantMatch(
  envelope: AnalystContextEnvelope,
  entityPlantId: string | undefined,
): boolean {
  if (!entityPlantId) return true;
  return entityPlantId === envelope.plantId;
}
