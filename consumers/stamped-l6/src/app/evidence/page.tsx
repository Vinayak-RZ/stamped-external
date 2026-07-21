import { AppShell } from "@/components/shell/AppShell";
import { PageHead, Panel } from "@/components/ui/primitives";
import { LoadDial } from "@/components/charts/LoadDial";
import { DEMO_PLANT, connectionFixture } from "@/fixtures/demo";

export default function EvidencePage() {
  return (
    <AppShell
      active="evidence"
      plantName={DEMO_PLANT.plantName}
      role="supervisor"
      connection={connectionFixture}
      screenTitle="Evidence explorer"
      contextSummary={["Pre-scoped charts", "Baseline bands in production via ECharts"]}
      criticalAlarmCount={2}
    >
      <PageHead eyebrow="Proof" title="Evidence explorer" />
      <Panel style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
        <LoadDial loadPct={108} label="Kiln 1" />
        <LoadDial loadPct={72} label="Mill 1" />
        <LoadDial loadPct={54} label="Compressor 2" />
        <p style={{ flex: "1 1 240px", fontSize: 13, color: "var(--forge-on-surface-variant)" }}>
          Production L6 mounts ECharts trend slices here with L2 baseline bands. This seed shows
          load dials adapted from the demo for asset state at a glance.
        </p>
      </Panel>
    </AppShell>
  );
}
