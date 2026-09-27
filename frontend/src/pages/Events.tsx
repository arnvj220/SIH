import { useEffect, useMemo, useState } from "react";
import { EventTimeline } from "../components/events/EventTimeline";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Empty, Loading } from "../components/ui/Empty";
import { api } from "../lib/api";
import { decisionTone, pct, timestamp, threatLabel } from "../lib/format";
import type { Event } from "../lib/types";
import { Page } from "../components/layout/Page";
import { invalidate } from "../lib/cache";

type EventFilter = "ALL" | "VERIFICATION" | "FLAGGED" | "SYSTEM";

function isVerification(event: Event): boolean {
  return event.event_type.toUpperCase() === "VERIFICATION";
}

function isFlagged(event: Event): boolean {
  const threats = event.details.threats;
  return event.details.decision === "REJECT" || (Array.isArray(threats) && threats.length > 0);
}

function eventTitle(event: Event): string {
  if (isVerification(event)) return "Verification attempt";
  return threatLabel(event.event_type);
}

function eventSummary(event: Event): string {
  if (!isVerification(event)) return "System activity recorded in the audit log.";
  const decision = String(event.details.decision ?? "UNKNOWN");
  const threats = Array.isArray(event.details.threats)
    ? event.details.threats.map(String)
    : [];
  if (threats.length > 0) return `${decision}: ${threats.map(threatLabel).join(", ")}`;
  return `${decision}: no threats detected`;
}

function detailValue(key: string, value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (key === "error_rate" && typeof value === "number") return pct(value);
  if (Array.isArray(value)) return value.length ? value.map(String).join(", ") : "None";
  if (typeof value === "object") return Object.entries(value as Record<string, unknown>)
    .map(([name, item]) => `${name}: ${String(item)}`)
    .join(" · ");
  return String(value);
}

export function Events() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selected, setSelected] = useState<Event | null>(null);
  const [filter, setFilter] = useState<EventFilter>("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  const refresh = async () => {
    invalidate("events");
    setLoading(true);
    setError(null);
    try {
      const latest = await api.listEvents();
      setEvents(latest);
      setSelected((current) =>
        current
          ? latest.find((event) => event.event_id === current.event_id) ?? latest[0] ?? null
          : latest[0] ?? null
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const clear = async () => {
    if (!confirm("Delete all events? This cannot be undone.")) return;
    setClearing(true);
    try {
      await api.clearEvents();
      setEvents([]);
      setSelected(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setClearing(false);
    }
  };

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return events.filter((event) => {
      if (filter === "VERIFICATION" && !isVerification(event)) return false;
      if (filter === "FLAGGED" && !isFlagged(event)) return false;
      if (filter === "SYSTEM" && isVerification(event)) return false;
      if (!query) return true;
      return [event.event_id, event.event_type, event.context_id ?? "", eventSummary(event)]
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }, [events, filter, search]);

  const verificationCount = events.filter(isVerification).length;
  const flaggedCount = events.filter(isFlagged).length;

  return (
    <Page
      title="Events"
      subtitle="A time-ordered audit trail of verification decisions and system activity. Select an event to inspect its recorded evidence."
      actions={
        <>
          <Button size="sm" variant="ghost" onClick={refresh} disabled={loading}>
            {loading ? "Loading..." : "Refresh"}
          </Button>
          <Button size="sm" variant="danger" disabled={clearing || events.length === 0} onClick={clear}>
            {clearing ? "Clearing..." : "Clear events"}
          </Button>
        </>
      }
    >
      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Summary label="Audit records" value={events.length} />
        <Summary label="Verification attempts" value={verificationCount} />
        <Summary label="Flagged outcomes" value={flaggedCount} tone={flaggedCount ? "danger" : "success"} />
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search event, ID, or outcome..."
          className="w-full max-w-sm rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-muted focus:border-primary focus:outline-none"
        />
        <div className="flex gap-1 overflow-x-auto rounded-md border border-border bg-surface p-1">
          {(["ALL", "VERIFICATION", "FLAGGED", "SYSTEM"] as EventFilter[]).map((item) => (
            <button
              key={item}
              aria-pressed={filter === item}
              onClick={() => setFilter(item)}
              className={`shrink-0 rounded px-2.5 py-1 text-xs ${filter === item ? "bg-primary/15 font-medium text-primary" : "text-muted hover:text-text"}`}
            >
              {item === "ALL" ? "All" : item === "VERIFICATION" ? "Verifications" : item === "FLAGGED" ? "Flagged" : "System"}
            </button>
          ))}
        </div>
        <span className="ml-auto text-xs text-muted">{filtered.length} shown</span>
      </div>

      {loading && events.length === 0 ? (
        <Loading label="Loading audit trail..." />
      ) : filtered.length === 0 ? (
        <Empty title="No matching events" hint="Adjust the filters or run a verification to create audit records." />
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
          <EventTimeline events={filtered} selectedId={selected?.event_id} onSelect={setSelected} />
          {selected ? <EventDetail event={selected} /> : <Empty title="Select an event" hint="Choose a timeline entry to inspect its recorded fields." />}
        </div>
      )}
    </Page>
  );
}

function Summary({ label, value, tone = "secondary" }: { label: string; value: number; tone?: "secondary" | "danger" | "success" }) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-xs text-muted">{label}</div>
          <div className="mt-1 font-mono text-2xl text-text">{value}</div>
        </div>
        <Badge tone={tone}>{tone === "danger" ? "REVIEW" : tone === "success" ? "CLEAR" : "LOGGED"}</Badge>
      </div>
    </Card>
  );
}

function EventDetail({ event }: { event: Event }) {
  const decision = String(event.details.decision ?? "");
  const threats = Array.isArray(event.details.threats) ? event.details.threats.map(String) : [];
  const entries = Object.entries(event.details).filter(([key]) => key !== "decision" && key !== "threats");

  return (
    <Card title={eventTitle(event)} subtitle={timestamp(event.created_at)}>
      <div className="flex flex-wrap gap-2">
        {decision && <Badge tone={decisionTone(decision)}>{decision}</Badge>}
        {threats.map((threat) => <Badge key={threat} tone="danger">{threatLabel(threat)}</Badge>)}
        {!decision && threats.length === 0 && <Badge tone="secondary">AUDIT EVENT</Badge>}
      </div>
      <p className="mt-3 text-sm leading-relaxed text-text">{eventSummary(event)}</p>
      <dl className="mt-4 space-y-3 border-t border-border pt-3">
        <DetailField label="Event ID" value={event.event_id} />
        <DetailField label="Related record" value={event.context_id ?? "Not linked"} />
        {entries.map(([key, value]) => (
          <DetailField key={key} label={threatLabel(key)} value={detailValue(key, value)} />
        ))}
      </dl>
    </Card>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] text-muted">{label}</dt>
      <dd className="mt-0.5 break-words font-mono text-xs text-text">{value}</dd>
    </div>
  );
}