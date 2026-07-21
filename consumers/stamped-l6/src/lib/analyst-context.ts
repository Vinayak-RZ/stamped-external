import type { AnalystContextEnvelope } from "./types";

export interface ContextChip {
  key: string;
  value: string;
}

/**
 * Build the user-visible context chips for Mode A analyst.
 * Strips excluded keys; never includes secrets.
 */
export function visibleContextChips(
  envelope: AnalystContextEnvelope,
): ContextChip[] {
  const excluded = new Set(envelope.excludeKeys ?? []);
  const candidates: ContextChip[] = [
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

  return candidates.filter((c) => c.value && !excluded.has(c.key));
}

/** Reject cross-tenant focus entities at the BFF boundary. */
export function assertTenantMatch(
  envelope: AnalystContextEnvelope,
  entityPlantId: string | undefined,
): boolean {
  if (!entityPlantId) return true;
  return entityPlantId === envelope.plantId;
}
