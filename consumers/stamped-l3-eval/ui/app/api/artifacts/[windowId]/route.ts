import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { goldenDir } from "@/lib/paths";

export const runtime = "nodejs";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ windowId: string }> },
) {
  const { windowId } = await ctx.params;
  const file = path.join(goldenDir(), `run_${windowId}.json`);
  if (!fs.existsSync(file)) {
    return NextResponse.json({ error: "artifact not found" }, { status: 404 });
  }
  const data = JSON.parse(fs.readFileSync(file, "utf-8"));
  return NextResponse.json(data);
}
