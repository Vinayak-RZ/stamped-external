import { NextResponse } from "next/server";
import fs from "fs";
import { corpusPath, goldenDir } from "@/lib/paths";
import path from "path";

export const runtime = "nodejs";

export async function GET() {
  const raw = fs.readFileSync(corpusPath(), "utf-8");
  const data = JSON.parse(raw) as {
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
  const windows = data.windows.map((w) => {
    const artPath = path.join(dir, `run_${w.window_id}.json`);
    let counts = { emitted: 0, suppressed: 0, shadow_only: 0 };
    if (fs.existsSync(artPath)) {
      const art = JSON.parse(fs.readFileSync(artPath, "utf-8")) as {
        detections: { status: string }[];
      };
      for (const d of art.detections) {
        if (d.status in counts) {
          counts[d.status as keyof typeof counts] += 1;
        }
      }
    }
    return { ...w, has_artifact: fs.existsSync(artPath), counts };
  });
  return NextResponse.json({ windows });
}
