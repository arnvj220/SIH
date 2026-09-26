// import { Badge } from "../ui/Badge";
import { timestamp } from "../../lib/format";
import type { Event } from "../../lib/types";

export function EventTimeline({ events }: { events: Event[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-border px-4 py-12 text-center text-sm text-muted">
        No events yet.
      </div>
    );
  }

  return (
    <ol className="relative border-l border-border pl-6">
      {events.map((e) => (
        <li key={e.event_id} className="mb-6 last:mb-0">
          <span className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-primary" />
          <div className="flex items-baseline justify-between gap-3">
            <div className="text-sm font-medium text-text">{e.event_type}</div>
            <span className="text-xs text-muted">{timestamp(e.created_at)}</span>
          </div>
          {e.context_id && (
            <div className="mt-1 text-xs text-muted font-mono">
              {e.context_id}
            </div>
          )}
          {Object.keys(e.details).length > 0 && (
            <details className="mt-2">
              <summary className="cursor-pointer text-xs text-muted">
                details
              </summary>
              <pre className="mt-1 overflow-auto rounded-md border border-border bg-bg p-2 text-[11px] font-mono text-muted">
                {JSON.stringify(e.details, null, 2)}
              </pre>
            </details>
          )}
        </li>
      ))}
    </ol>
  );
}