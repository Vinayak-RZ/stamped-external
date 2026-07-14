"use client";

import { useCallback, useEffect, useState } from "react";
import type { RunArtifact } from "@/lib/types";
import { WindowForensic } from "@/components/WindowForensic";

export function LiveClient() {
  const [data, setData] = useState<(RunArtifact & { connected?: boolean; error?: string }) | null>(
    null,
  );
  const [busy, setBusy] = useState(false);

  const poll = useCallback(async () => {
    setBusy(true);
    try {
      const res = await fetch("/api/live", { cache: "no-store" });
      const json = await res.json();
      setData(json);
    } catch (e) {
      setData({ error: String(e), connected: false } as never);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 4000);
    return () => clearInterval(id);
  }, [poll]);

  const connected = Boolean(data && "detections" in data && data.connected !== false);

  return (
    <>
      <div className="filters">
        <button type="button" onClick={poll} disabled={busy}>
          Refresh
        </button>
        <span>
          {connected ? (
            <>
              <span className="live-pulse" aria-hidden />
              Connected to CORE_LAB_URL
            </>
          ) : (
            <span style={{ color: "var(--lab-muted)" }}>
              {data?.error || "Set CORE_LAB_URL to attach to core lab export"}
            </span>
          )}
        </span>
      </div>
      {data && "detections" in data && Array.isArray(data.detections) ? (
        <WindowForensic artifact={data as RunArtifact} />
      ) : (
        <div className="empty">
          Live attach polls <code>CORE_LAB_URL/lab/export</code>. Start core lab server or use offline
          Corpus views.
        </div>
      )}
    </>
  );
}
