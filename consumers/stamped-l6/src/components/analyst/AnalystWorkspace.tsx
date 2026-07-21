import { Panel } from "@/components/ui/primitives";

/** Mode B full analyst workspace shell — live L4 wiring is consumer P1. */
export function AnalystWorkspace() {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "220px 1.4fr 1fr",
        gap: 12,
        minHeight: 480,
      }}
      className="analyst-grid"
    >
      <Panel>
        <h2 style={{ margin: "0 0 12px", fontSize: 14, fontFamily: "var(--forge-font-display)" }}>
          Investigations
        </h2>
        <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, lineHeight: 1.7 }}>
          <li>Kiln 1 MD coincidence</li>
          <li>Mill 1 PF slab</li>
          <li>New investigation…</li>
        </ul>
      </Panel>

      <Panel style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <h2 style={{ margin: 0, fontSize: 14, fontFamily: "var(--forge-font-display)" }}>
          Conversation
        </h2>
        <div
          style={{
            flex: 1,
            background: "var(--forge-surface-low)",
            borderRadius: 8,
            padding: 12,
            fontSize: 13,
            color: "var(--forge-on-surface-variant)",
          }}
        >
          Full analyst uses L4 ReAct with citations. Fixture shell only — connect HTTP in P1.
        </div>
        <input
          aria-label="Ask full analyst"
          placeholder="Investigate across the plant…"
          style={{
            border: "1px solid var(--forge-outline-variant)",
            borderRadius: 8,
            padding: "10px 12px",
            fontSize: 13,
          }}
        />
      </Panel>

      <Panel>
        <h2 style={{ margin: "0 0 12px", fontSize: 14, fontFamily: "var(--forge-font-display)" }}>
          Sources & evidence
        </h2>
        <p style={{ margin: 0, fontSize: 13, color: "var(--forge-on-surface-variant)" }}>
          Citations, Path H / Path W labels, and evidence canvas land here. Handoff-to-action always
          confirms before L5 writes.
        </p>
      </Panel>

      <style>{`
        @media (max-width: 1100px) {
          .analyst-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
