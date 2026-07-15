import fs from "fs";
import path from "path";
import { goldenDir } from "@/lib/paths";
import type { Detection, RunArtifact } from "@/lib/types";
import { DetectorsClient } from "./DetectorsClient";

export const dynamic = "force-dynamic";

export default function DetectorsPage() {
  const dir = goldenDir();
  const rows: (Detection & { window_id: string; run_id: string })[] = [];
  if (fs.existsSync(dir)) {
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
      const art = JSON.parse(
        fs.readFileSync(path.join(dir, f), "utf-8"),
      ) as RunArtifact;
      for (const d of art.detections) {
        rows.push({ ...d, window_id: art.window_id, run_id: art.run_id });
      }
    }
  }
  rows.sort(
    (a, b) =>
      a.category.localeCompare(b.category) || a.status.localeCompare(b.status),
  );

  return (
    <>
      <h1>Detectors</h1>
      <p className="lede">
        Every engine, rule, and ML-shadow candidate across golden artifacts —
        filter by L4 vs Lab-only lane (ADR-015).
      </p>
      {rows.length === 0 ? (
        <div className="empty">
          No artifacts yet. Run <code>stamped-l3-eval lab-run --window w-md-001</code>
        </div>
      ) : (
        <DetectorsClient rows={rows} />
      )}
    </>
  );
}
