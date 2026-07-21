/**
 * Industrial load dial — adapted from stamped-energy-dashboard LoadDial.jsx.
 */
export function LoadDial({
  loadPct,
  label,
}: {
  loadPct: number;
  label: string;
}) {
  const clamped = Math.max(0, Math.min(120, loadPct));
  const angle = -125 + (clamped / 120) * 250;
  const tone =
    clamped >= 100 ? "var(--forge-error)" : clamped >= 85 ? "var(--forge-warning)" : "var(--forge-tertiary)";

  return (
    <div
      role="img"
      aria-label={`${label} load ${Math.round(loadPct)} percent`}
      style={{ width: 120, textAlign: "center" }}
    >
      <svg width={120} height={90} viewBox="0 0 120 90" aria-hidden>
        <path
          d="M 20 75 A 40 40 0 1 1 100 75"
          fill="none"
          stroke="var(--forge-surface-low)"
          strokeWidth={10}
          strokeLinecap="round"
        />
        <path
          d="M 20 75 A 40 40 0 1 1 100 75"
          fill="none"
          stroke={tone}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={`${(clamped / 120) * 188} 188`}
        />
        <line
          x1={60}
          y1={70}
          x2={60}
          y2={38}
          stroke="var(--forge-secondary)"
          strokeWidth={3}
          strokeLinecap="round"
          transform={`rotate(${angle} 60 70)`}
        />
      </svg>
      <div
        className="tabular"
        style={{ fontFamily: "var(--forge-font-display)", fontWeight: 700, fontSize: 16 }}
      >
        {Math.round(loadPct)}%
      </div>
      <div style={{ fontSize: 12, color: "var(--forge-on-surface-variant)" }}>{label}</div>
    </div>
  );
}
