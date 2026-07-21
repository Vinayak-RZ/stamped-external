/**
 * Circular gauge — adapted from stamped-energy-dashboard Gauge.jsx.
 * Pure SVG; provide accessible text via `label` + `valueText`.
 */
export function Gauge({
  value,
  max = 100,
  size = 88,
  label,
  valueText,
}: {
  value: number;
  max?: number;
  size?: number;
  label: string;
  valueText: string;
}) {
  const pct = Math.max(0, Math.min(1, value / max));
  const r = (size - 12) / 2;
  const c = 2 * Math.PI * r;
  const dash = c * pct;

  return (
    <div
      role="img"
      aria-label={`${label}: ${valueText}`}
      style={{ width: size, height: size, position: "relative" }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--forge-surface-low)"
          strokeWidth={8}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--forge-tertiary)"
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c - dash}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div
        className="tabular"
        style={{
          position: "absolute",
          inset: 0,
          display: "grid",
          placeItems: "center",
          fontFamily: "var(--forge-font-display)",
          fontWeight: 800,
          fontSize: size * 0.22,
        }}
      >
        {valueText}
      </div>
    </div>
  );
}
