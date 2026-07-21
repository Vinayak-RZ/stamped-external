import { AppShell } from "@/components/shell/AppShell";
import { PageHead, Panel, StatusChip } from "@/components/ui/primitives";
import { claimBadgeLabel, formatInr } from "@/lib/format";
import { DEMO_PLANT, connectionFixture, prescriptionsFixture } from "@/fixtures/demo";

export default function ReportsPage() {
  const closed = prescriptionsFixture.filter((p) => p.lane === "closed");

  return (
    <AppShell
      active="reports"
      plantName={DEMO_PLANT.plantName}
      role="plant_head"
      connection={connectionFixture}
      screenTitle="Reports and ledger"
      contextSummary={["Ops-confirmed ledger", "Export centre entry"]}
      criticalAlarmCount={2}
    >
      <PageHead eyebrow="Exports" title="Ledger snapshot" />
      <Panel>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr>
              <th scope="col" style={{ textAlign: "left", padding: 8 }}>
                Prescription
              </th>
              <th scope="col" style={{ textAlign: "right", padding: 8 }}>
                Realised
              </th>
              <th scope="col" style={{ textAlign: "left", padding: 8 }}>
                Claim
              </th>
            </tr>
          </thead>
          <tbody>
            {closed.map((p) => {
              const badge = claimBadgeLabel(p.verificationStatus);
              return (
                <tr key={p.id} style={{ borderTop: "1px solid var(--forge-outline-variant)" }}>
                  <td style={{ padding: 8 }}>{p.title}</td>
                  <td className="tabular" style={{ padding: 8, textAlign: "right" }}>
                    {formatInr(p.realisedInr ?? 0)}
                  </td>
                  <td style={{ padding: 8 }}>
                    <StatusChip tone={badge.tone}>{badge.label}</StatusChip>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Panel>
    </AppShell>
  );
}
