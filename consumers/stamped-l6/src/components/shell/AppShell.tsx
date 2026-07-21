"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { ConnectionStatus, NavKey, Role } from "@/lib/types";
import { GhostButton, PrimaryButton } from "@/components/ui/primitives";
import { ContextualAnalyst } from "@/components/analyst/ContextualAnalyst";

const PRIMARY: Array<{ key: NavKey; href: string; label: string }> = [
  { key: "today", href: "/", label: "Today" },
  { key: "alarms", href: "/alarms", label: "Alarms" },
  { key: "prescriptions", href: "/prescriptions", label: "Prescriptions" },
  { key: "evidence", href: "/evidence", label: "Evidence" },
  { key: "analyst", href: "/analyst", label: "Analyst" },
  { key: "reports", href: "/reports", label: "Reports" },
];

const REVEAL: Array<{ key: NavKey; href: string; label: string }> = [
  { key: "energy", href: "/energy", label: "Energy" },
  { key: "equipment", href: "/equipment", label: "Equipment" },
  { key: "intensity", href: "/intensity", label: "Intensity / CO₂" },
  { key: "integrations", href: "/settings/integrations", label: "Integrations" },
  { key: "admin", href: "/settings/admin", label: "Admin" },
];

export function AppShell({
  active,
  plantName,
  role,
  connection,
  screenTitle,
  contextSummary,
  focusEntity,
  criticalAlarmCount,
  children,
}: {
  active: NavKey;
  plantName: string;
  role: Role;
  connection: ConnectionStatus;
  screenTitle: string;
  contextSummary: string[];
  focusEntity?: { type: "alarm" | "prescription" | "asset" | "ledger_entry"; id: string };
  criticalAlarmCount: number;
  children: React.ReactNode;
}) {
  const [revealed, setRevealed] = useState(false);
  const [analystOpen, setAnalystOpen] = useState(false);

  const sseLabel = useMemo(() => {
    if (connection.sse === "live") return "Live";
    if (connection.sse === "reconnecting") return "Reconnecting";
    return "Offline";
  }, [connection.sse]);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header
        style={{
          background: "var(--forge-secondary)",
          color: "#fff",
          padding: "12px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <strong style={{ fontFamily: "var(--forge-font-display)", fontSize: 16 }}>
            Stamped Energy
          </strong>
          <span style={{ opacity: 0.85, fontSize: 13 }}>{plantName}</span>
          <span
            aria-live="polite"
            style={{
              fontSize: 12,
              padding: "4px 8px",
              borderRadius: 999,
              background:
                connection.sse === "live"
                  ? "rgba(0,102,107,0.35)"
                  : "rgba(201,122,0,0.35)",
            }}
          >
            SSE {sseLabel}
          </span>
        </div>
        <PrimaryButton onClick={() => setAnalystOpen(true)}>Ask Analyst</PrimaryButton>
      </header>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <nav
          aria-label="Primary"
          style={{
            width: 220,
            flexShrink: 0,
            background: "var(--forge-surface-lowest)",
            borderRight: "1px solid var(--forge-outline-variant)",
            padding: 12,
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {PRIMARY.map((item) => (
            <Link
              key={item.key}
              href={item.href}
              aria-current={active === item.key ? "page" : undefined}
              style={{
                padding: "10px 12px",
                borderRadius: 8,
                fontWeight: active === item.key ? 700 : 500,
                background: active === item.key ? "var(--forge-primary-dim)" : "transparent",
                color:
                  active === item.key ? "var(--forge-primary)" : "var(--forge-on-surface)",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <span>{item.label}</span>
              {item.key === "alarms" && criticalAlarmCount > 0 ? (
                <span className="tabular" aria-label={`${criticalAlarmCount} critical`}>
                  {criticalAlarmCount}
                </span>
              ) : null}
            </Link>
          ))}

          <GhostButton onClick={() => setRevealed((v) => !v)}>
            {revealed ? "Hide tools" : "More tools"}
          </GhostButton>

          {revealed
            ? REVEAL.map((item) => (
                <Link
                  key={item.key}
                  href={item.href}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 8,
                    fontSize: 13,
                    color: "var(--forge-on-surface-variant)",
                  }}
                >
                  {item.label}
                </Link>
              ))
            : null}

          <p style={{ marginTop: "auto", fontSize: 11, color: "var(--forge-on-surface-variant)" }}>
            Role: {role.replace("_", " ")}
          </p>
        </nav>

        <main
          style={{
            flex: 1,
            overflow: "auto",
            padding: "20px 16px",
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          {connection.sse !== "live" ? (
            <div
              role="status"
              style={{
                padding: "10px 14px",
                borderRadius: 8,
                background: "rgba(201,122,0,0.14)",
                color: "var(--forge-warning)",
                fontWeight: 600,
                fontSize: 13,
              }}
            >
              Live updates paused — {sseLabel.toLowerCase()}. Actions still work; lists may be stale.
            </div>
          ) : null}
          {children}
        </main>
      </div>

      <ContextualAnalyst
        open={analystOpen}
        onClose={() => setAnalystOpen(false)}
        envelope={{
          orgId: "org_demo",
          plantId: "plant_jaipur_01",
          userId: "user_demo",
          role,
          routeId: active,
          screenTitle,
          focusEntity,
          visibleSummary: contextSummary,
        }}
      />
    </div>
  );
}
