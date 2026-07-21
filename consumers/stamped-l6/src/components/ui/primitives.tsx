import type { CSSProperties, ReactNode } from "react";

const toneBg: Record<string, string> = {
  critical: "rgba(186, 26, 26, 0.12)",
  warning: "rgba(201, 122, 0, 0.14)",
  good: "rgba(0, 102, 107, 0.12)",
  neutral: "rgba(143, 112, 107, 0.16)",
  info: "rgba(143, 112, 107, 0.16)",
};

const toneFg: Record<string, string> = {
  critical: "var(--forge-error)",
  warning: "var(--forge-warning)",
  good: "var(--forge-tertiary)",
  neutral: "var(--forge-on-surface-variant)",
  info: "var(--forge-on-surface-variant)",
};

export function StatusChip({
  tone,
  children,
}: {
  tone: keyof typeof toneBg;
  children: ReactNode;
}) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 600,
        padding: "3px 9px",
        background: toneBg[tone] ?? toneBg.neutral,
        color: toneFg[tone] ?? toneFg.neutral,
      }}
    >
      {children}
    </span>
  );
}

export function Panel({
  children,
  style,
  as: Tag = "section",
}: {
  children: ReactNode;
  style?: CSSProperties;
  as?: "section" | "div" | "article";
}) {
  return (
    <Tag
      style={{
        background: "var(--forge-surface-lowest)",
        border: "1px solid var(--forge-outline-variant)",
        borderRadius: "var(--forge-radius-lg)",
        padding: 20,
        ...style,
      }}
    >
      {children}
    </Tag>
  );
}

export function PageHead({
  eyebrow,
  title,
  actions,
}: {
  eyebrow?: string;
  title: string;
  actions?: ReactNode;
}) {
  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: 16,
        alignItems: "flex-end",
        flexWrap: "wrap",
      }}
    >
      <div>
        {eyebrow ? (
          <p
            style={{
              margin: 0,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              color: "var(--forge-on-surface-variant)",
            }}
          >
            {eyebrow}
          </p>
        ) : null}
        <h1
          style={{
            margin: "4px 0 0",
            fontFamily: "var(--forge-font-display)",
            fontSize: 28,
            fontWeight: 700,
          }}
        >
          {title}
        </h1>
      </div>
      {actions}
    </header>
  );
}

export function PrimaryButton({
  children,
  onClick,
  type = "button",
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        minHeight: 48,
        padding: "0 18px",
        borderRadius: "var(--forge-radius-md)",
        background: disabled ? "var(--forge-outline)" : "var(--forge-primary)",
        color: "#fff",
        fontWeight: 600,
        fontSize: 14,
      }}
    >
      {children}
    </button>
  );
}

export function GhostButton({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        minHeight: 44,
        padding: "0 14px",
        borderRadius: "var(--forge-radius-md)",
        border: "1px solid var(--forge-outline-variant)",
        color: "var(--forge-secondary)",
        fontWeight: 600,
        fontSize: 13,
      }}
    >
      {children}
    </button>
  );
}
