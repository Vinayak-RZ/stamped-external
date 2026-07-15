import fs from "fs";
import path from "path";
import Link from "next/link";
import { goldenDir } from "@/lib/paths";
import { WindowForensic } from "@/components/WindowForensic";
import type { RunArtifact } from "@/lib/types";
import { countByDelivery, countByStatus } from "@/lib/status";

export const dynamic = "force-dynamic";

export default async function WindowPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const file = path.join(goldenDir(), `run_${id}.json`);
  if (!fs.existsSync(file)) {
    return (
      <>
        <h1>Window {id}</h1>
        <div className="empty">
          No RunArtifact for this window. Generate one:
          <br />
          <code>stamped-l3-eval lab-run --window {id}</code>
          <br />
          <Link href="/corpus">Back to corpus</Link>
        </div>
      </>
    );
  }
  const artifact = JSON.parse(fs.readFileSync(file, "utf-8")) as RunArtifact;
  const counts = countByStatus(artifact.detections);
  const lanes = countByDelivery(artifact.detections);

  return (
    <>
      <h1>{artifact.window_id}</h1>
      <p className="lede">
        run <span className="mono">{artifact.run_id}</span> · plant{" "}
        <span className="mono">{artifact.plant_id}</span> · core {artifact.core_version} ·{" "}
        schema {artifact.schema_version} · {lanes.l4} L4 · {lanes.lab_only} Lab-only ·{" "}
        {counts.emitted} emitted · {counts.suppressed} suppressed · {counts.shadow_only}{" "}
        shadow · {counts.hypothesis} hypothesis
      </p>
      <WindowForensic artifact={artifact} />
    </>
  );
}
