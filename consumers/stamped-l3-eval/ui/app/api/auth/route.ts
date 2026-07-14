import { NextResponse } from "next/server";
import { AUTH_COOKIE, expectedToken } from "@/lib/auth";

export async function POST(req: Request) {
  const secret = process.env.LAB_SHARED_SECRET;
  const body = (await req.json().catch(() => ({}))) as { secret?: string };
  if (!secret) {
    const res = NextResponse.json({ ok: true, mode: "open" });
    return res;
  }
  if (!body.secret || body.secret !== secret) {
    return NextResponse.json({ error: "invalid secret" }, { status: 401 });
  }
  const res = NextResponse.json({ ok: true });
  res.cookies.set(AUTH_COOKIE, expectedToken(secret), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 12,
  });
  return res;
}
