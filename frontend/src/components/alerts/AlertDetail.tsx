import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Table } from "../ui/Table";
import { timestamp, threatLabel } from "../../lib/format";
import type { Alert } from "../../lib/types";

interface Props {
  alert: Alert;
  onResolve: () => void;
  resolving: boolean;
}

interface EvidenceRow {
  type?: string;
  rule_id?: string;
  observed?: unknown;
  threshold?: unknown;
  explanation?: string;
}

function displayEvidenceValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return text.length > 40 ? `${text.slice(0, 18)}...${text.slice(-10)}` : text;
}

export function AlertDetail({ alert, onResolve, resolving }: Props) {
  const evidenceRows: EvidenceRow[] = Array.isArray(alert.evidence)
    ? alert.evidence.filter(
        (item): item is EvidenceRow => !!item && typeof item === "object"
      )
    : [];

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

      <div className="mt-4 grid grid-cols-1 gap-2 border-t border-border pt-3 sm:grid-cols-2">
        <ContextValue label="Verification" value={alert.verification_id} />
        <ContextValue label="Attack run" value={alert.attack_id} />
      </div>

      {alert.description && (
        <div className="mt-4 border-l-2 border-danger px-3 py-2">
          <div className="text-[11px] font-semibold uppercase text-danger">Why it was flagged</div>
          <p className="mt-1 text-sm leading-relaxed text-text">{alert.description}</p>
        </div>
      )}

      {alert.evidence !== null && alert.evidence !== undefined && (
        <div className="mt-4 space-y-2">
          <div>
            <div className="text-xs font-semibold text-text">Detection evidence</div>
            <p className="mt-0.5 text-[11px] text-muted">Observed values compared with the detector's expected value or threshold.</p>
          </div>
          <Table<EvidenceRow>
            rows={evidenceRows}
            rowKey={(_, index) => `${alert.alert_id}-evidence-${index}`}
            empty="No structured evidence recorded."
            columns={[
              {
                key: "type",
                header: "Signal",
                render: (row) => (
                  <span className="font-mono text-xs text-primary">{row.type ?? "—"}</span>
                ),
              },
              {
                key: "rule_id",
                header: "Rule",
                render: (row) => (
                  <span className="font-mono text-[11px] text-text">{row.rule_id ?? "—"}</span>
                ),
              },
              {
                key: "observed",
                header: "Observed value",
                render: (row) => (
                  <span className="break-all font-mono text-xs text-text" title={displayEvidenceValue(row.observed)}>
                    {displayEvidenceValue(row.observed)}
                  </span>
                ),
              },
              {
                key: "threshold",
                header: "Expected value",
                render: (row) => (
                  <span className="break-all font-mono text-xs text-muted">
                    {displayEvidenceValue(row.threshold)}
                  </span>
                ),
              },
              {
                key: "explanation",
                header: "Explanation",
                render: (row) => (
                  <span className="text-xs text-muted">{row.explanation ?? "—"}</span>
                ),
              },
            ]}
          />
          <details>
            <summary className="cursor-pointer text-xs text-muted">Raw evidence</summary>
            <pre className="mt-2 max-h-64 overflow-auto rounded-md border border-border bg-bg p-3 text-[11px] font-mono text-muted">
              {JSON.stringify(alert.evidence, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </Card>
  );
}

function ContextValue({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="min-w-0">
      <div className="text-[11px] text-muted">{label}</div>
      <div className="break-all font-mono text-xs text-text">{value ?? "Not linked"}</div>
    </div>
  );
}