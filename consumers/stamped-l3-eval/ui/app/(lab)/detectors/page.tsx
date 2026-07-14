import fs from "fs";
import path from "path";
import Link from "next/link";
import { goldenDir } from "@/lib/paths";
import type { Detection, RunArtifact } from "@/lib/types";
import { statusLabel } from "@/lib/status";

export const dynamic = "force-dynamic";

export default function DetectorsPage() {
  const dir = goldenDir();
  const rows: (Detection & { window_id: string; run_id: string })[] = [];
  if (fs.existsSync(dir)) {
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
      const art = JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")) as RunArtifact;
      for (const d of art.detections) {
        rows.push({ ...d, window_id: art.window_id, run_id: art.run_id });
      }
    }
  }
  rows.sort((a, b) => a.category.localeCompare(b.category) || a.status.localeCompare(b.status));

  return (
    <>
      <h1>Detectors</h1>
      <p className="lede">
        Every engine, rule, and ML-shadow candidate across golden artifacts — browse by category
        and rulepack URI.
      </p>
      {rows.length === 0 ? (
        <div className="empty">
          No artifacts yet. Run <code>stamped-l3-eval lab-run --window w-md-001</code>
        </div>
      ) : (
        <table className="data">
          <thead>
            <tr>
              <th>Category</th>
              <th>Kind</th>
              <th>Status</th>
              <th>Ref</th>
              <th>Window</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={`${r.run_id}-${r.detection_id}`}>
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
      )}
    </>
  );
}
