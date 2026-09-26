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