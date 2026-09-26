import { useEffect, useState } from "react";
import { EventTimeline } from "../components/events/EventTimeline";
import { Button } from "../components/ui/Button";
import { api } from "../lib/api";
import type { Event } from "../lib/types";

export function Events() {
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  const refresh = () =>
    api.listEvents().then(setEvents).catch((e) => setError(String(e)));

  useEffect(() => {
    refresh();
  }, []);

  const clear = async () => {
    if (!confirm("Delete all events? This cannot be undone.")) return;
    setClearing(true);
    try {
      await api.clearEvents();
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text">Events</h1>
          <p className="mt-1 text-sm text-muted">
            Chronological audit log of verification and attack activity.
          </p>
        </div>
        <Button size="sm" variant="ghost" onClick={clear} disabled={clearing}>
          {clearing ? "…" : "Clear all"}
        </Button>
      </header>

      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <EventTimeline events={events} />
    </div>
  );
}