"use client";

import { useMemo, useState } from "react";
import type { Prescription, PrescriptionLane } from "@/lib/types";
import { claimBadgeLabel, formatInr } from "@/lib/format";
import { GhostButton, Panel, PrimaryButton, StatusChip } from "@/components/ui/primitives";

const LANES: PrescriptionLane[] = ["needs_review", "active", "verifying", "closed"];

const laneLabel: Record<PrescriptionLane, string> = {
  needs_review: "Needs review",
  active: "Active",
  verifying: "Verifying",
  closed: "Closed",
};

export function PrescriptionQueue({ initial }: { initial: Prescription[] }) {
  const [rows, setRows] = useState(initial);
  const [lane, setLane] = useState<PrescriptionLane>("needs_review");
  const [deferId, setDeferId] = useState<string | null>(null);
  const [reason, setReason] = useState("");

  const sorted = useMemo(() => {
    return rows
      .filter((r) => r.lane === lane)
      .sort((a, b) => b.impactInrPerMonth * b.confidence - a.impactInrPerMonth * a.confidence);
  }, [rows, lane]);

  const openInr = rows
    .filter((r) => r.lane === "needs_review" || r.lane === "active")
    .reduce((s, r) => s + r.impactInrPerMonth, 0);

  function defer(id: string) {
    if (!reason.trim()) return;
    setRows((all) => all.filter((r) => r.id !== id));
    setDeferId(null);
    setReason("");
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Panel style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <p style={{ margin: 0, fontSize: 12, color: "var(--forge-on-surface-variant)" }}>
            Addressable open queue
          </p>
          <p
            className="tabular"
            style={{
              margin: "4px 0 0",
              fontFamily: "var(--forge-font-display)",
              fontWeight: 800,
              fontSize: 28,
            }}
          >
            {formatInr(openInr)}/mo
          </p>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {LANES.map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLane(l)}
              aria-pressed={lane === l}
              style={{
                minHeight: 40,
                padding: "0 12px",
                borderRadius: 8,
                fontWeight: 600,
                fontSize: 13,
                background: lane === l ? "var(--forge-secondary)" : "var(--forge-surface-low)",
                color: lane === l ? "#fff" : "var(--forge-on-surface)",
              }}
            >
              {laneLabel[l]}
            </button>
          ))}
        </div>
      </Panel>

      {sorted.length === 0 ? (
        <Panel>
          <p style={{ margin: 0 }}>Nothing in {laneLabel[lane]}.</p>
        </Panel>
      ) : (
        sorted.map((rx) => {
          const badge = claimBadgeLabel(rx.verificationStatus);
          return (
            <Panel key={rx.id} as="article">
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <h3 style={{ margin: 0, fontFamily: "var(--forge-font-display)", fontSize: 17 }}>
                    {rx.title}
                  </h3>
                  <p style={{ margin: "6px 0 0", fontSize: 13, color: "var(--forge-on-surface-variant)" }}>
                    {rx.why}
                  </p>
                </div>
                <p
                  className="tabular"
                  style={{ margin: 0, fontFamily: "var(--forge-font-display)", fontWeight: 800, fontSize: 20 }}
                >
                  {formatInr(rx.impactInrPerMonth)}/mo
                </p>
              </div>

              <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap", alignItems: "center" }}>
                <StatusChip tone="info">{Math.round(rx.confidence * 100)}% confidence</StatusChip>
                {rx.verificationStatus ? (
                  <StatusChip tone={badge.tone}>{badge.label}</StatusChip>
                ) : null}
              </div>

              {rx.opportunityCost ? (
                <p style={{ margin: "12px 0 0", fontSize: 12, color: "var(--forge-warning)" }}>
                  Delay cost {formatInr(rx.opportunityCost.modeledInr)} over{" "}
                  {rx.opportunityCost.delayDays} days. Modeled — not bill-verified.
                </p>
              ) : null}

              {lane === "needs_review" || lane === "active" ? (
                <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
                  <PrimaryButton
                    onClick={() =>
                      setRows((all) =>
                        all.map((r) =>
                          r.id === rx.id ? { ...r, lane: "verifying", verificationStatus: "pending" } : r,
                        ),
                      )
                    }
                  >
                    Mark done
                  </PrimaryButton>
                  <GhostButton onClick={() => setDeferId(rx.id)}>Defer…</GhostButton>
                  <GhostButton>Show proof</GhostButton>
                </div>
              ) : null}

              {deferId === rx.id ? (
                <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
                  <label htmlFor={`reason-${rx.id}`} style={{ fontSize: 12, fontWeight: 600 }}>
                    Defer reason (required)
                  </label>
                  <textarea
                    id={`reason-${rx.id}`}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    rows={2}
                    style={{
                      width: "100%",
                      borderRadius: 8,
                      border: "1px solid var(--forge-outline-variant)",
                      padding: 10,
                      fontFamily: "inherit",
                    }}
                  />
                  <PrimaryButton onClick={() => defer(rx.id)} disabled={!reason.trim()}>
                    Confirm defer
                  </PrimaryButton>
                </div>
              ) : null}
            </Panel>
          );
        })
      )}
    </div>
  );
}
