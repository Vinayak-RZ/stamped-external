import { PrescriptionQueue } from "@/components/prescriptions/PrescriptionQueue";
import { AppShell } from "@/components/shell/AppShell";
import { PageHead } from "@/components/ui/primitives";
import { DEMO_PLANT, connectionFixture, prescriptionsFixture } from "@/fixtures/demo";

export default function PrescriptionsPage() {
  return (
    <AppShell
      active="prescriptions"
      plantName={DEMO_PLANT.plantName}
      role="supervisor"
      connection={connectionFixture}
      screenTitle="Prescription queue"
      contextSummary={["₹-sorted triage", "Ops-confirmed badges"]}
      focusEntity={{ type: "prescription", id: prescriptionsFixture[0].id }}
      criticalAlarmCount={2}
    >
      <PageHead eyebrow="Closure" title="Prescription queue" />
      <PrescriptionQueue initial={prescriptionsFixture} />
    </AppShell>
  );
}
