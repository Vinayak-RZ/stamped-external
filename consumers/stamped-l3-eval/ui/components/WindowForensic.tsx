"use client";

import { useMemo, useState } from "react";
import type { Detection, RunArtifact } from "@/lib/types";
import {
  deliveryLabel,
  isAttributionScores,
  statusLabel,
} from "@/lib/status";

export function WindowForensic({ artifact }: { artifact: RunArtifact }) {
  const [laneFilter, setLaneFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Detection | null>(
    artifact.detections[0] ?? null,
  );

  const rows = useMemo(() => {
    return artifact.detections.filter((d) => {
      if (laneFilter === "l4" && d.delivery !== "l4") return false;
      if (laneFilter === "lab_only" && d.delivery !== "lab_only") return false;
      if (statusFilter !== "all" && d.status !== statusFilter) return false;
      if (!query) return true;
      const q = query.toLowerCase();
      return (
        d.rule_or_model_ref.toLowerCase().includes(q) ||
        d.category.toLowerCase().includes(q) ||
        d.detector_kind.toLowerCase().includes(q)
      );
    });
  }, [artifact.detections, laneFilter, statusFilter, query]);

  const scores = selected?.scores;
  const showAttr = isAttributionScores(scores);

  return (
    <>
      <div className="filters">
        <select
          value={laneFilter}
          onChange={(e) => setLaneFilter(e.target.value)}
          aria-label="Lane filter"
        >
          <option value="all">All lanes</option>
          <option value="l4">L4 delivery</option>
          <option value="lab_only">Lab-only discovery</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Status filter"
        >
          <option value="all">All statuses</option>
          <option value="emitted">Emitted</option>
          <option value="suppressed">Suppressed</option>
          <option value="shadow_only">Shadow</option>
          <option value="hypothesis">Hypothesis</option>
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
                <th>Lane</th>
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
                    <span className={`chip delivery-${d.delivery}`}>
                      {deliveryLabel(d.delivery)}
                    </span>
                  </td>
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
                <span className={`chip delivery-${selected.delivery}`}>
                  {deliveryLabel(selected.delivery)}
                </span>{" "}
                <span className={`chip ${selected.status}`}>
                  {statusLabel(selected.status)}
                </span>
                {typeof selected.scores?.agree_with_primary === "boolean" ? (
                  <>
                    {" "}
                    <span
                      className={`chip ${
                        selected.scores.agree_with_primary
                          ? "agree"
                          : "disagree"
                      }`}
                    >
                      {selected.scores.agree_with_primary
                        ? "Shadow agrees"
                        : "Shadow disagrees"}
                    </span>
                  </>
                ) : null}
              </p>
              <p className="mono">{selected.rule_or_model_ref}</p>
              <p>
                <strong>Suppressions</strong>
                <br />
                {selected.suppressions_checked.join(", ") || "—"}
              </p>
              {showAttr ? (
                <div className="attr-block">
                  <p>
                    <strong>Attribution explainability</strong>
                  </p>
                  <p className="mono" style={{ color: "var(--lab-muted)" }}>
                    score = ramp_kw × 1/(1+hops)
                  </p>
                  <ul className="mono">
                    {"ramp_kw" in (scores || {}) ? (
                      <li>ramp_kw: {String(scores?.ramp_kw)}</li>
                    ) : null}
                    {"hops" in (scores || {}) ? (
                      <li>hops: {String(scores?.hops)}</li>
                    ) : null}
                    {"proximity" in (scores || {}) ? (
                      <li>proximity: {String(scores?.proximity)}</li>
                    ) : null}
                    {"score" in (scores || {}) ? (
                      <li>score: {String(scores?.score)}</li>
                    ) : null}
                    {"rank" in (scores || {}) ? (
                      <li>rank: {String(scores?.rank)}</li>
                    ) : null}
                    {"shadow_method" in (scores || {}) ? (
                      <li>shadow_method: {String(scores?.shadow_method)}</li>
                    ) : null}
                    {"corr_abs" in (scores || {}) ? (
                      <li>corr_abs: {String(scores?.corr_abs)}</li>
                    ) : null}
                  </ul>
                </div>
              ) : null}
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
