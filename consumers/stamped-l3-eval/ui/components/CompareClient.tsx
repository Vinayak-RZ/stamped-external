"use client";

import { useMemo, useState } from "react";
import type { RunArtifact } from "@/lib/types";
import { statusLabel } from "@/lib/status";

export function CompareClient({ artifacts }: { artifacts: RunArtifact[] }) {
  const [leftId, setLeftId] = useState(artifacts[0]?.run_id ?? "");
  const [rightId, setRightId] = useState(artifacts[1]?.run_id ?? artifacts[0]?.run_id ?? "");

  const left = artifacts.find((a) => a.run_id === leftId);
  const right = artifacts.find((a) => a.run_id === rightId);

  const diff = useMemo(() => {
    if (!left || !right) return { onlyLeft: [], onlyRight: [], both: [] as string[] };
    const l = new Set(left.detections.filter((d) => d.status === "emitted").map((d) => d.rule_or_model_ref));
    const r = new Set(right.detections.filter((d) => d.status === "emitted").map((d) => d.rule_or_model_ref));
    return {
      onlyLeft: [...l].filter((x) => !r.has(x)),
      onlyRight: [...r].filter((x) => !l.has(x)),
      both: [...l].filter((x) => r.has(x)),
    };
  }, [left, right]);

  if (artifacts.length === 0) {
    return <div className="empty">Need golden artifacts to compare runs.</div>;
  }

  return (
    <>
      <div className="filters">
        <label>
          Left{" "}
          <select value={leftId} onChange={(e) => setLeftId(e.target.value)}>
            {artifacts.map((a) => (
              <option key={a.run_id} value={a.run_id}>
                {a.window_id} · {a.run_id}
              </option>
            ))}
          </select>
        </label>
        <label>
          Right{" "}
          <select value={rightId} onChange={(e) => setRightId(e.target.value)}>
            {artifacts.map((a) => (
              <option key={a.run_id} value={a.run_id}>
                {a.window_id} · {a.run_id}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="forensic" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
        <section className="panel">
          <h2>Only left (emitted)</h2>
          <ul>
            {diff.onlyLeft.map((x) => (
              <li key={x} className="mono">
                {x}
              </li>
            ))}
          </ul>
        </section>
        <section className="panel">
          <h2>Both</h2>
          <ul>
            {diff.both.map((x) => (
              <li key={x} className="mono">
                {x}
              </li>
            ))}
          </ul>
        </section>
        <section className="panel">
          <h2>Only right (emitted)</h2>
          <ul>
            {diff.onlyRight.map((x) => (
              <li key={x} className="mono">
                {x}
              </li>
            ))}
          </ul>
        </section>
      </div>
      {left && right ? (
        <p className="lede" style={{ marginTop: "1rem" }}>
          Left {left.detections.length} detections ({left.detections.map((d) => statusLabel(d.status)).join(", ")}) ·
          Right {right.detections.length} detections
        </p>
      ) : null}
    </>
  );
}
