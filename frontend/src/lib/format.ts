export function pct(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return `${(x * 100).toFixed(digits)}%`;
}

export function ms(x: number | null | undefined, digits = 3): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return `${x.toFixed(digits)} ms`;
}

export function num(
  x: number | null | undefined,
  digits = 4
): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return x.toFixed(digits);
}

export function int(x: number | null | undefined): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return String(Math.round(x));
}

export function timestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function threatLabel(t: string): string {
  return t.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

export function decisionTone(
  d: string
): "success" | "warning" | "danger" | "muted" {
  switch (d) {
    case "ACCEPT":
      return "success";
    case "SUSPICIOUS":
      return "warning";
    case "REJECT":
      return "danger";
    default:
      return "muted";
  }
}