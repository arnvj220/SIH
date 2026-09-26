import { Badge } from "../ui/Badge";
import { Table } from "../ui/Table";
import { timestamp, threatLabel } from "../../lib/format";
import type { Alert } from "../../lib/types";

interface Props {
  alerts: Alert[];
  onSelect: (alert: Alert) => void;
  selectedId?: string;
}

export function AlertList({ alerts, onSelect, selectedId }: Props) {
  return (
    <Table<Alert>
      rows={alerts}
      rowKey={(a) => a.alert_id}
      empty="No alerts yet."
      columns={[
        {
          key: "type",
          header: "Type",
          render: (a) => (
            <button
              onClick={() => onSelect(a)}
              className={
                a.alert_id === selectedId
                  ? "font-medium text-primary"
                  : "text-text hover:text-primary"
              }
            >
              {threatLabel(a.alert_type)}
            </button>
          ),
        },
        {
          key: "severity",
          header: "Severity",
          render: (a) => {
  let t: "danger" | "warning" | "muted" = "muted";
  if (a.severity === "CRITICAL" || a.severity === "HIGH") t = "danger";
  else if (a.severity === "MEDIUM") t = "warning";
  return <Badge tone={t}>{a.severity}</Badge>;
},
        },
        {
          key: "status",
          header: "Status",
          render: (a) => <Badge tone="muted">{a.status}</Badge>,
        },
        {
          key: "created",
          header: "Created",
          align: "right",
          render: (a) => (
            <span className="text-xs text-muted">{timestamp(a.created_at)}</span>
          ),
        },
      ]}
    />
  );
}