"use client";

import { useMemo, useState } from "react";
import type { Detection, RunArtifact } from "@/lib/types";
import { statusLabel } from "@/lib/status";

export function WindowForensic({ artifact }: { artifact: RunArtifact }) {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Detection | null>(
    artifact.detections[0] ?? null,
  );

  const rows = useMemo(() => {
    return artifact.detections.filter((d) => {
      if (statusFilter !== "all" && d.status !== statusFilter) return false;
      if (!query) return true;
      const q = query.toLowerCase();
      return (
        d.rule_or_model_ref.toLowerCase().includes(q) ||
        d.category.toLowerCase().includes(q) ||
        d.detector_kind.toLowerCase().includes(q)
      );
    });
  }, [artifact.detections, statusFilter, query]);

  return (
    <>
      <div className="filters">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Status filter"
        >
          <option value="all">All statuses</option>
          <option value="emitted">Emitted</option>
          <option value="suppressed">Suppressed</option>
          <option value="shadow_only">Shadow</option>
        </select>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter category / rule / engine"
          aria-label="Text filter"
          style={{ minWidth: "16rem" }}
        />
      </div>
      <div className="forensic">
        <aside className="panel">
          <h2>Timeline</h2>
          {artifact.timeline.map((t, i) => (
            <div key={`${t.ts}-${i}`} className="timeline-item">
              <div className="mono" style={{ color: "var(--lab-muted)" }}>
                {t.ts}
              </div>
              <div>
                <strong>{t.step}</strong> — {t.detail}
              </div>
            </div>
          ))}
        </aside>
        <section className="panel">
          <h2>Detections</h2>
          <table className="data">
            <thead>
              <tr>
                <th>Status</th>
                <th>Kind</th>
                <th>Category</th>
                <th>Ref</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((d) => (
                <tr
                  key={d.detection_id}
                  data-selected={selected?.detection_id === d.detection_id}
                  onClick={() => setSelected(d)}
                  style={{ cursor: "pointer" }}
                >
                  <td>
                    <span className={`chip ${d.status}`}>{statusLabel(d.status)}</span>
                  </td>
                  <td>{d.detector_kind}</td>
                  <td>{d.category}</td>
                  <td className="mono">{d.rule_or_model_ref}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <p className="empty">No detections match this filter.</p>
          ) : null}
        </section>
        <aside className="panel">
          <h2>Inspector</h2>
          {selected ? (
            <>
              <p>
                <span className={`chip ${selected.status}`}>
                  {statusLabel(selected.status)}
                </span>
              </p>
              <p className="mono">{selected.rule_or_model_ref}</p>
              <p>
                <strong>Suppressions</strong>
                <br />
                {selected.suppressions_checked.join(", ") || "—"}
              </p>
              <p>
                <strong>Scores</strong>
                <br />
                <span className="mono">
                  {selected.scores ? JSON.stringify(selected.scores) : "—"}
                </span>
              </p>
              <p>
                <strong>Logs</strong>
              </p>
              <ul>
                {selected.logs.map((l, i) => (
                  <li key={i} className="mono">
                    {l}
                  </li>
                ))}
              </ul>
              {selected.finding ? (
                <>
                  <p>
                    <strong>Finding</strong>
                  </p>
                  <pre className="mono" style={{ whiteSpace: "pre-wrap" }}>
                    {JSON.stringify(selected.finding, null, 2)}
                  </pre>
                </>
              ) : null}
            </>
          ) : (
            <p className="empty">Select a detection row.</p>
          )}
        </aside>
      </div>
    </>
  );
}
