import Link from "next/link";
import fs from "fs";
import path from "path";
import { corpusPath, goldenDir } from "@/lib/paths";

export const dynamic = "force-dynamic";

export default function CorpusPage() {
  const data = JSON.parse(fs.readFileSync(corpusPath(), "utf-8")) as {
    windows: {
      window_id: string;
      category: string;
      plant_id: string;
      asset: string;
      window: string;
      rulepack_ref: string;
    }[];
  };
  const dir = goldenDir();

  return (
    <>
      <h1>Corpus</h1>
      <p className="lede">Gold windows and linked RunArtifacts — one job: pick a window to inspect.</p>
      <table className="data">
        <thead>
          <tr>
            <th>Window</th>
            <th>Plant</th>
            <th>Category</th>
            <th>Hits</th>
            <th>Artifact</th>
          </tr>
        </thead>
        <tbody>
          {data.windows.map((w) => {
            const art = path.join(dir, `run_${w.window_id}.json`);
            let hits = "—";
            if (fs.existsSync(art)) {
              const a = JSON.parse(fs.readFileSync(art, "utf-8"));
              const e = a.detections.filter((d: { status: string }) => d.status === "emitted").length;
              const s = a.detections.filter((d: { status: string }) => d.status === "suppressed").length;
              const sh = a.detections.filter((d: { status: string }) => d.status === "shadow_only").length;
              hits = `${e}E / ${s}S / ${sh}Sh`;
            }
            return (
              <tr key={w.window_id}>
                <td>
                  <Link href={`/windows/${w.window_id}`}>{w.window_id}</Link>
                </td>
                <td className="mono">{w.plant_id}</td>
                <td>{w.category}</td>
                <td className="mono">{hits}</td>
                <td>{fs.existsSync(art) ? "yes" : "missing"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}
