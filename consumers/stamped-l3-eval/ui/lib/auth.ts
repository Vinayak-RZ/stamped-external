import { createHash } from "crypto";

export const AUTH_COOKIE = "lab_auth";

export function expectedToken(secret: string): string {
  return createHash("sha256").update(secret).digest("hex");
}

export function isAuthorized(cookieValue: string | undefined, secret: string | undefined): boolean {
  // ponytail: unset secret allows local/CI build; deploy must set LAB_SHARED_SECRET
  if (!secret) return true;
  if (!cookieValue) return false;
  return cookieValue === expectedToken(secret);
}
