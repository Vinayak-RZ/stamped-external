"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import type { AnalystContextEnvelope } from "@/lib/types";
import { visibleContextChips } from "@/lib/analyst-context";
import { GhostButton, PrimaryButton } from "@/components/ui/primitives";

export function ContextualAnalyst({
  open,
  onClose,
  envelope,
}: {
  open: boolean;
  onClose: () => void;
  envelope: AnalystContextEnvelope;
}) {
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);
  const [excluded, setExcluded] = useState<string[]>([]);
  const [draft, setDraft] = useState("");

  const chips = useMemo(
    () => visibleContextChips({ ...envelope, excludeKeys: excluded }),
    [envelope, excluded],
  );

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(5,31,19,0.45)",
          zIndex: 40,
        }}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          height: "100vh",
          width: 380,
          maxWidth: "92vw",
          background: "var(--forge-surface-lowest)",
          boxShadow: "var(--forge-shadow-panel)",
          zIndex: 50,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            background: "var(--forge-secondary)",
            color: "#fff",
            padding: 16,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <h2 id={titleId} style={{ margin: 0, fontSize: 15, fontFamily: "var(--forge-font-display)" }}>
              Stamped Analyst
            </h2>
            <p style={{ margin: "4px 0 0", fontSize: 11, opacity: 0.85 }}>
              Context from this screen · RAG via L4
            </p>
          </div>
          <button
            ref={closeRef}
            type="button"
            aria-label="Close analyst"
            onClick={onClose}
            style={{ color: "#fff", fontSize: 18, padding: 8 }}
          >
            ×
          </button>
        </div>

        <div style={{ padding: 14, borderBottom: "1px solid var(--forge-outline-variant)" }}>
          <p style={{ margin: "0 0 8px", fontSize: 12, fontWeight: 600 }}>Attached context</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {chips.length === 0 ? (
              <span style={{ fontSize: 12, color: "var(--forge-on-surface-variant)" }}>
                No context attached
              </span>
            ) : (
              chips.map((chip) => (
                <button
                  key={chip.key}
                  type="button"
                  onClick={() => setExcluded((prev) => [...prev, chip.key])}
                  title="Remove from context"
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    padding: "4px 8px",
                    borderRadius: 999,
                    background: "var(--forge-primary-dim)",
                    color: "var(--forge-primary)",
                  }}
                >
                  {chip.value} ×
                </button>
              ))
            )}
          </div>
        </div>

        <div style={{ flex: 1, padding: 16, overflow: "auto", fontSize: 13, lineHeight: 1.5 }}>
          <p style={{ margin: 0, color: "var(--forge-on-surface-variant)" }}>
            Ask about this screen. Answers cite L4 retrieval; irreversible plant actions always need
            your confirm.
          </p>
        </div>

        <div style={{ padding: 14, borderTop: "1px solid var(--forge-outline-variant)" }}>
          <label className="sr-only" htmlFor="analyst-input">
            Ask Stamped Analyst
          </label>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              id="analyst-input"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Ask about this screen…"
              style={{
                flex: 1,
                border: "1px solid var(--forge-outline-variant)",
                borderRadius: 8,
                padding: "10px 12px",
                fontSize: 13,
              }}
            />
            <PrimaryButton
              onClick={() => {
                // ponytail: fixture send — wire L4 HTTP in consumer P1
                setDraft("");
              }}
            >
              Send
            </PrimaryButton>
          </div>
          <div style={{ marginTop: 10 }}>
            <GhostButton onClick={onClose}>Done</GhostButton>
          </div>
        </div>
      </aside>
    </>
  );
}
