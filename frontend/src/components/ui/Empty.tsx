import type { ReactNode } from "react";

export function Empty({
  title,
  hint,
}: {
  title: string;
  hint?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border px-6 py-12 text-center">
      <div className="text-sm font-medium text-text">{title}</div>
      {hint && <div className="text-xs text-muted max-w-md">{hint}</div>}
    </div>
  );
}

export function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border px-6 py-12 text-center">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-border border-t-primary" />
      <div className="text-xs text-muted">{label}</div>
    </div>
  );
}