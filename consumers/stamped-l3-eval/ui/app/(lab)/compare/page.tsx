import fs from "fs";
import path from "path";
import { goldenDir } from "@/lib/paths";
import type { RunArtifact } from "@/lib/types";
import { CompareClient } from "@/components/CompareClient";

export const dynamic = "force-dynamic";

export default function ComparePage() {
  const dir = goldenDir();
  const artifacts: RunArtifact[] = [];
  if (fs.existsSync(dir)) {
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
      artifacts.push(JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")));
    }
  }

  return (
    <>
      <h1>Compare</h1>
      <p className="lede">Diff emitted rule/model refs between two RunArtifact runs.</p>
      <CompareClient artifacts={artifacts} />
    </>
  );
}
