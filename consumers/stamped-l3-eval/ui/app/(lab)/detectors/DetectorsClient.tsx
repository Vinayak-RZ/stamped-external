"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Detection } from "@/lib/types";
import { deliveryLabel, statusLabel } from "@/lib/status";

type Row = Detection & { window_id: string; run_id: string };

export function DetectorsClient({ rows }: { rows: Row[] }) {
  const [lane, setLane] = useState("all");
  const filtered = useMemo(() => {
    if (lane === "all") return rows;
    return rows.filter((r) => r.delivery === lane);
  }, [rows, lane]);

  return (
    <>
      <div className="filters">
        <select
          value={lane}
          onChange={(e) => setLane(e.target.value)}
          aria-label="Lane filter"
        >
          <option value="all">All lanes</option>
          <option value="l4">L4 delivery</option>
          <option value="lab_only">Lab-only discovery</option>
        </select>
      </div>
      <table className="data">
        <thead>
          <tr>
            <th>Lane</th>
            <th>Category</th>
            <th>Kind</th>
            <th>Status</th>
            <th>Ref</th>
            <th>Window</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((r) => (
            <tr key={`${r.run_id}-${r.detection_id}`}>
              <td>
                <span className={`chip delivery-${r.delivery}`}>
                  {deliveryLabel(r.delivery)}
                </span>
              </td>
              <td>{r.category}</td>
              <td>{r.detector_kind}</td>
              <td>
                <span className={`chip ${r.status}`}>{statusLabel(r.status)}</span>
              </td>
              <td className="mono">{r.rule_or_model_ref}</td>
              <td>
                <Link href={`/windows/${r.window_id}`}>{r.window_id}</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {filtered.length === 0 ? (
        <p className="empty">No detections in this lane.</p>
      ) : null}
    </>
  );
}
