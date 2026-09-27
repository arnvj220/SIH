import { useEffect, useMemo, useState } from "react";
import { AlertList } from "../components/alerts/AlertList";
import { AlertDetail } from "../components/alerts/AlertDetail";
import { Empty, Loading } from "../components/ui/Empty";
import { Page } from "../components/layout/Page";
import { api } from "../lib/api";
import type { Alert } from "../lib/types";
import { invalidate } from "../lib/cache";
import { Button } from "../components/ui/Button";

type SeverityFilter = "ALL" | "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selected, setSelected] = useState<Alert | null>(null);
  const [resolving, setResolving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sev, setSev] = useState<SeverityFilter>("ALL");

  const refresh = async () => {
    setLoading(true);
    try {
      const latest = await api.listAlerts();
      setAlerts(latest);
      setSelected((current) =>
        current
          ? latest.find((alert) => alert.alert_id === current.alert_id) ?? latest[0] ?? null
          : latest[0] ?? null
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const resolve = async () => {
    if (!selected) return;
    setResolving(true);
    try {
      const updated = await api.resolveAlert(selected.alert_id);
      setSelected(updated);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setResolving(false);
    }
  };

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return alerts.filter((a) => {
      if (sev !== "ALL" && a.severity !== sev) return false;
      if (!q) return true;
      return (
        a.title.toLowerCase().includes(q) ||
        a.alert_type.toLowerCase().includes(q) ||
        a.alert_id.toLowerCase().includes(q) ||
        a.description?.toLowerCase().includes(q) ||
        a.verification_id?.toLowerCase().includes(q)
      );
    });
  }, [alerts, sev, search]);

  const counts = useMemo(() => {
    const c: Record<string, number> = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
    };
    for (const a of alerts) c[a.severity] = (c[a.severity] ?? 0) + 1;
    return c;
  }, [alerts]);

  const openCount = alerts.filter((a) => a.status !== "RESOLVED").length;

  return (
    <Page
      title="Alerts"
      subtitle="Investigate detected threats, their evidence, and the verification each alert belongs to."
      actions={
        <Button
          size="sm"
          variant="ghost"
          onClick={() => {
            invalidate("alerts");
            refresh();
          }}
        >
          Refresh
        </Button>
      }
    >

      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      {loading && alerts.length === 0 ? (
        <Loading label="Fetching alerts..." />
      ) : (
        <>
          {/* Severity ribbon */}
          <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-5">
            <RibbonStat label="Total" value={alerts.length} />
            <RibbonStat label="Open" value={openCount} tone="warning" />
            <RibbonStat label="Critical" value={counts.CRITICAL} tone="danger" />
            <RibbonStat label="High" value={counts.HIGH} tone="danger" />
            <RibbonStat label="Medium" value={counts.MEDIUM} tone="warning" />
          </div>

      {/* Filter bar */}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
            placeholder="Search alert, threat, or verification..."
            className="w-full max-w-md rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-muted focus:border-primary focus:outline-none"
        />
        <div className="flex items-center gap-1 rounded-md border border-border bg-bg p-0.5">
          {(["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"] as SeverityFilter[]).map(
            (s) => (
              <button
                key={s}
                onClick={() => setSev(s)}
                aria-pressed={sev === s}
                className={
                  "rounded px-2.5 py-1 text-xs font-medium transition-colors " +
                  (sev === s
                    ? "bg-primary/15 text-primary"
                    : "text-muted hover:text-text")
                }
              >
                {s}
              </button>
            )
          )}
        </div>
        <span className="ml-auto text-xs text-muted">
          Showing {filtered.length} of {alerts.length}
        </span>
      </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
            <AlertList
              alerts={filtered}
              onSelect={setSelected}
              selectedId={selected?.alert_id}
            />
            <div>
              {selected ? (
                <AlertDetail
                  alert={selected}
                  onResolve={resolve}
                  resolving={resolving}
                />
              ) : (
                <Empty title="No alert selected" hint="Pick a row to see details." />
              )}
            </div>
          </div>
        </>
      )}
    </Page>
  );
}

function RibbonStat({
  label,
  value,
  tone = "muted",
}: {
  label: string;
  value: number;
  tone?: "danger" | "warning" | "success" | "muted";
}) {
  const toneClass =
    tone === "danger"
      ? "text-danger border-danger/30 bg-danger/5"
      : tone === "warning"
        ? "text-warning border-warning/30 bg-warning/5"
        : tone === "success"
          ? "text-success border-success/30 bg-success/5"
          : "text-text border-border bg-surface";
  return (
    <div className={`rounded-lg border px-4 py-3 ${toneClass}`}>
      <div className="text-[11px] uppercase tracking-wider opacity-80">
        {label}
      </div>
      <div className="mt-1 font-mono text-2xl">{value}</div>
    </div>
  );
}