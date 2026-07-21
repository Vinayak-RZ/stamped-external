import { AppShell } from "@/components/shell/AppShell";
import { TodayBoard } from "@/components/today/TodayBoard";
import { PageHead } from "@/components/ui/primitives";
import {
  DEMO_PLANT,
  connectionFixture,
  todaySignalsFixture,
} from "@/fixtures/demo";

export default function TodayPage() {
  return (
    <AppShell
      active="today"
      plantName={DEMO_PLANT.plantName}
      role="plant_head"
      connection={connectionFixture}
      screenTitle="Today at the plant"
      contextSummary={["2 critical alarms", "₹2.14L open prescriptions", "Telemetry fresh"]}
      criticalAlarmCount={2}
    >
      <PageHead eyebrow="Ops home" title="Today at the plant" />
      <TodayBoard signals={todaySignalsFixture} closurePct={64} />
    </AppShell>
  );
}
