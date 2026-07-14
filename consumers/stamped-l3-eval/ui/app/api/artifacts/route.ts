import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { goldenDir } from "@/lib/paths";

export const runtime = "nodejs";

export async function GET() {
  const dir = goldenDir();
  if (!fs.existsSync(dir)) {
    return NextResponse.json({ artifacts: [] });
  }
  const artifacts = fs
    .readdirSync(dir)
    .filter((f) => f.startsWith("run_") && f.endsWith(".json"))
    .map((f) => {
      const data = JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8"));
      return {
        file: f,
        run_id: data.run_id,
        window_id: data.window_id,
        plant_id: data.plant_id,
        detection_count: data.detections?.length ?? 0,
      };
    });
  return NextResponse.json({ artifacts });
}
