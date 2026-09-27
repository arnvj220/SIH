import { Badge } from "../ui/Badge";

interface Props {
  runId: string;
  config: Record<string, unknown>;
  metrics: Record<string, unknown>;
}

export function RunFooter({ runId, config, metrics }: Props) {
  const seed = config.seed;
  const nTargets = config.n_targets;
  const rounds = config.rounds;
  const attack = config.attack_type;
  const latency = metrics.latency_mean_ms;

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 rounded-md border border-border bg-bg/40 px-3 py-2 text-[11px] text-muted">
      <span className="font-mono">
        <span className="text-muted">run=</span>
        <span className="text-primary">{runId}</span>
      </span>
      <span className="font-mono">
        attack=<span className="text-text">{String(attack ?? "—")}</span>
      </span>
      <span className="font-mono">
        seed=<span className="text-text">{String(seed ?? "—")}</span>
      </span>
      <span className="font-mono">
        targets=<span className="text-text">{String(nTargets ?? "—")}</span>
      </span>
      <span className="font-mono">
        rounds=<span className="text-text">{String(rounds ?? "—")}</span>
      </span>
      {typeof latency === "number" && (
        <span className="font-mono">
          latency=<span className="text-text">{latency.toFixed(2)}ms</span>
        </span>
      )}
      <Badge tone="muted">Reproducible</Badge>
    </div>
  );
}