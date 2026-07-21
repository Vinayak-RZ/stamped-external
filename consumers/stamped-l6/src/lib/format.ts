/** Indian-locale formatters for L6 surfaces. */

export function formatInr(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatIndianNum(n: number, digits = 0): string {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: digits,
  }).format(n);
}

export function claimBadgeLabel(
  status: string | undefined,
): { label: string; tone: "good" | "warning" | "neutral" | "critical" } {
  switch (status) {
    case "ops_confirmed":
      return { label: "Ops-confirmed", tone: "good" };
    case "modeled":
      return { label: "Modeled — not bill-verified", tone: "warning" };
    case "pending":
      return { label: "Pending", tone: "neutral" };
    case "disputed":
      return { label: "Disputed", tone: "critical" };
    case "verified":
      // Reserved for future bill path — never invent from ops alone.
      return { label: "Bill-verified", tone: "good" };
    default:
      return { label: "Unknown", tone: "neutral" };
  }
}
