import { useEffect, useState } from "react";
import { AlertList } from "../components/alerts/AlertList";
import { AlertDetail } from "../components/alerts/AlertDetail";
import { Empty } from "../components/ui/Empty";
import { api } from "../lib/api";
import type { Alert } from "../lib/types";

export function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selected, setSelected] = useState<Alert | null>(null);
  const [resolving, setResolving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () =>
    api.listAlerts().then(setAlerts).catch((e) => setError(String(e)));

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

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <header className="mb-6">
        <h1 className="text-xl font-semibold text-text">Alerts</h1>
        <p className="mt-1 text-sm text-muted">
          Threat detections persisted by the verification engine.
        </p>
      </header>

      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_420px]">
        <AlertList
          alerts={alerts}
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
    </div>
  );
}