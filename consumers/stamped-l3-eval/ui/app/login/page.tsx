"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function LoginForm() {
  const [secret, setSecret] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/corpus";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ secret }),
    });
    if (!res.ok) {
      setError("Invalid lab secret");
      return;
    }
    router.replace(next);
  }

  return (
    <form className="login" onSubmit={onSubmit}>
      <h1>L3 Eval Lab</h1>
      <p className="lede">Internal access — enter LAB_SHARED_SECRET</p>
      <input
        type="password"
        name="secret"
        autoComplete="current-password"
        value={secret}
        onChange={(e) => setSecret(e.target.value)}
        placeholder="Shared secret"
        required
      />
      <button type="submit">Enter lab</button>
      {error ? <p style={{ color: "var(--status-error)" }}>{error}</p> : null}
    </form>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<p className="lede">Loading…</p>}>
      <LoginForm />
    </Suspense>
  );
}
