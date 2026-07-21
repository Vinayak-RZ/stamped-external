import { AnalystWorkspace } from "@/components/analyst/AnalystWorkspace";
import { AppShell } from "@/components/shell/AppShell";
import { PageHead } from "@/components/ui/primitives";
import { DEMO_PLANT, connectionFixture } from "@/fixtures/demo";

export default function AnalystPage() {
  return (
    <AppShell
      active="analyst"
      plantName={DEMO_PLANT.plantName}
      role="energy_manager"
      connection={connectionFixture}
      screenTitle="Full analyst workspace"
      contextSummary={["Mode B workspace", "Citations required"]}
      criticalAlarmCount={2}
    >
      <PageHead
        eyebrow="Analyst · Mode B"
        title="Investigation workspace"
      />
      <AnalystWorkspace />
    </AppShell>
  );
}
