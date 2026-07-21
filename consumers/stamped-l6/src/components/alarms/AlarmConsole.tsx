"use client";

import { useMemo, useState } from "react";
import type { Alarm } from "@/lib/types";
import { GhostButton, Panel, PrimaryButton, StatusChip } from "@/components/ui/primitives";

const severityTone = {
  critical: "critical",
  warning: "warning",
  info: "info",
} as const;

export function AlarmConsole({ initial }: { initial: Alarm[] }) {
  const [alarms, setAlarms] = useState(initial);
  const [selected, setSelected] = useState(0);

  const open = useMemo(
    () => alarms.filter((a) => a.state !== "cleared"),
    [alarms],
  );

  const current = open[selected] ?? open[0];

  function ack(id: string) {
    setAlarms((rows) =>
      rows.map((a) => (a.id === id ? { ...a, state: "acked", ownerRole: "supervisor" } : a)),
    );
  }

  if (open.length === 0) {
    return (
      <Panel>
        <p style={{ margin: 0 }}>No open alarms — plant looks calm.</p>
      </Panel>
    );
  }

  return (
    <div
      style={{ display: "grid", gridTemplateColumns: "minmax(240px, 1fr) 1.4fr", gap: 16 }}
      className="alarm-grid"
    >
      <Panel style={{ padding: 0, overflow: "hidden" }}>
        <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {open.map((a, i) => (
            <li key={a.id}>
              <button
                type="button"
                onClick={() => setSelected(i)}
                aria-current={current?.id === a.id ? "true" : undefined}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "12px 14px",
                  borderBottom: "1px solid var(--forge-outline-variant)",
                  background:
                    current?.id === a.id ? "var(--forge-primary-dim)" : "transparent",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <strong style={{ fontSize: 13 }}>{a.assetLabel}</strong>
                  <StatusChip tone={severityTone[a.severity]}>{a.severity}</StatusChip>
                </div>
                <p
                  style={{
                    margin: "6px 0 0",
                    fontSize: 12,
                    color: "var(--forge-on-surface-variant)",
                  }}
                >
                  {a.state} · {a.summary}
                </p>
              </button>
            </li>
          ))}
        </ul>
      </Panel>

      {current ? (
        <Panel>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
            <div>
              <h2 style={{ margin: 0, fontFamily: "var(--forge-font-display)", fontSize: 20 }}>
                {current.assetLabel}
              </h2>
              <p style={{ margin: "6px 0 0", fontSize: 14 }}>{current.summary}</p>
            </div>
            <StatusChip tone={severityTone[current.severity]}>{current.state}</StatusChip>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
            {current.state === "raised" ? (
              <PrimaryButton onClick={() => ack(current.id)}>Ack alarm</PrimaryButton>
            ) : null}
            <GhostButton>Open evidence</GhostButton>
            {current.relatedPrescriptionId ? (
              <GhostButton>Open Rx {current.relatedPrescriptionId}</GhostButton>
            ) : null}
          </div>
          <p style={{ margin: "16px 0 0", fontSize: 12, color: "var(--forge-on-surface-variant)" }}>
            Keyboard: j/k move · a ack · e evidence (wired in consumer). Lifecycle truth lives in L5.
          </p>
        </Panel>
      ) : null}

      <style>{`
        @media (max-width: 900px) {
          .alarm-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
