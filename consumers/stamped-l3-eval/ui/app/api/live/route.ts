import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET() {
  const base = process.env.CORE_LAB_URL;
  if (!base) {
    return NextResponse.json(
      { error: "CORE_LAB_URL not configured", connected: false },
      { status: 503 },
    );
  }
  const token = process.env.CORE_LAB_TOKEN || "";
  const endpoint = base.replace(/\/$/, "") + "/lab/export";
  try {
    const resp = await fetch(endpoint, {
      headers: {
        Accept: "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      cache: "no-store",
    });
    if (!resp.ok) {
      return NextResponse.json(
        { error: `core lab ${resp.status}`, connected: false },
        { status: 502 },
      );
    }
    const data = await resp.json();
    return NextResponse.json({ connected: true, ...data });
  } catch (err) {
    return NextResponse.json(
      { error: String(err), connected: false },
      { status: 502 },
    );
  }
}
