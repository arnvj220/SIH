import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { timestamp, threatLabel } from "../../lib/format";
import type { Alert } from "../../lib/types";

interface Props {
  alert: Alert;
  onResolve: () => void;
  resolving: boolean;
}

export function AlertDetail({ alert, onResolve, resolving }: Props) {
  return (
    <Card
      title={alert.title}
      subtitle={threatLabel(alert.alert_type)}
      action={
        alert.status !== "RESOLVED" ? (
          <Button size="sm" variant="ghost" onClick={onResolve} disabled={resolving}>
            {resolving ? "…" : "Resolve"}
          </Button>
        ) : (
          <Badge tone="success">RESOLVED</Badge>
        )
      }
    >
      <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
        <dt className="text-muted">Alert ID</dt>
        <dd className="font-mono text-text">{alert.alert_id}</dd>
        <dt className="text-muted">Severity</dt>
        <dd>
          <Badge
  tone={
    alert.severity === "CRITICAL" || alert.severity === "HIGH"
      ? "danger"
      : alert.severity === "MEDIUM"
        ? "warning"
        : "muted"
  }
>
  {alert.severity}
</Badge>
        </dd>
        <dt className="text-muted">Status</dt>
        <dd>{alert.status}</dd>
        <dt className="text-muted">Created</dt>
        <dd className="text-text">{timestamp(alert.created_at)}</dd>
        {alert.resolved_at && (
          <>
            <dt className="text-muted">Resolved</dt>
            <dd className="text-text">{timestamp(alert.resolved_at)}</dd>
          </>
        )}
      </dl>

      {alert.description && (
        <p className="mt-4 text-sm text-text">{alert.description}</p>
      )}

      {alert.evidence !== null && alert.evidence !== undefined && (
        <details className="mt-4">
          <summary className="cursor-pointer text-xs font-medium text-muted">
            Evidence
          </summary>
          <pre className="mt-2 overflow-auto rounded-md border border-border bg-bg p-3 text-[11px] font-mono text-muted">
            {JSON.stringify(alert.evidence, null, 2)}
          </pre>
        </details>
      )}
    </Card>
  );
}