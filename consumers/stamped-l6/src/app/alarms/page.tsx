import { AlarmConsole } from "@/components/alarms/AlarmConsole";
import { AppShell } from "@/components/shell/AppShell";
import { PageHead } from "@/components/ui/primitives";
import { DEMO_PLANT, alarmsFixture, connectionFixture } from "@/fixtures/demo";

export default function AlarmsPage() {
  const critical = alarmsFixture.filter(
    (a) => a.severity === "critical" && a.state !== "cleared",
  ).length;

  return (
    <AppShell
      active="alarms"
      plantName={DEMO_PLANT.plantName}
      role="supervisor"
      connection={connectionFixture}
      screenTitle="EMS alarm console"
      contextSummary={["Open EMS alarms", "Severity-first triage"]}
      focusEntity={{ type: "alarm", id: alarmsFixture[0].id }}
      criticalAlarmCount={critical}
    >
      <PageHead eyebrow="EMS" title="Alarm console" />
      <AlarmConsole initial={alarmsFixture} />
    </AppShell>
  );
}
