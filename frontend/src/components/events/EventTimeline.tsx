import { Badge } from "../ui/Badge";
import { decisionTone, pct, timestamp, threatLabel } from "../../lib/format";
import type { Event } from "../../lib/types";

interface Props {
  events: Event[];
  selectedId?: string;
  onSelect: (event: Event) => void;
}

export function EventTimeline({ events, selectedId, onSelect }: Props) {
  if (events.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-border bg-surface px-4 py-12 text-center text-sm text-muted">
        No events yet.
      </div>
    );
  }

  return (
    <ol className="relative border-l border-border pl-6">
      {events.map((e) => (
        <li key={e.event_id} className="relative mb-3 last:mb-0">
          <span className="absolute -left-[30px] top-1.5 h-3 w-3 rounded-full bg-primary" />
          <button
            type="button"
            aria-pressed={e.event_id === selectedId}
            onClick={() => onSelect(e)}
            className={`w-full rounded-md border p-3 text-left transition-colors ${e.event_id === selectedId ? "border-primary/60 bg-primary/5" : "border-border bg-surface hover:bg-bg/60"}`}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="text-sm font-semibold text-text">
                {e.event_type.toUpperCase() === "VERIFICATION" ? "Verification attempt" : threatLabel(e.event_type)}
              </div>
              <div className="flex items-center gap-2">
                {typeof e.details.decision === "string" && (
                  <Badge tone={decisionTone(e.details.decision)}>{e.details.decision}</Badge>
                )}
                <span className="text-xs text-muted">{timestamp(e.created_at)}</span>
              </div>
            </div>
            {Array.isArray(e.details.threats) && e.details.threats.length > 0 ? (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {e.details.threats.map((threat) => (
                  <Badge key={String(threat)} tone="danger">{threatLabel(String(threat))}</Badge>
                ))}
              </div>
            ) : e.details.decision === "ACCEPT" ? (
              <div className="mt-2 text-xs text-success">No threats detected</div>
            ) : null}
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted">
              {typeof e.details.signer_id === "string" && typeof e.details.verifier_id === "string" && (
                <span>{e.details.signer_id} <span aria-hidden="true">→</span> {e.details.verifier_id}</span>
              )}
              {typeof e.details.error_rate === "number" && <span>Error rate {pct(e.details.error_rate)}</span>}
              {e.context_id && <span className="font-mono">{e.context_id}</span>}
            </div>
          </button>
        </li>
      ))}
    </ol>
  );
}