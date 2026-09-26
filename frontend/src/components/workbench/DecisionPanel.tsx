import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";

interface Props {
  decision?: string;
  threats?: string[];
  evidence?: unknown[];
}

type Tone = "success" | "warning" | "danger" | "muted";

export function DecisionPanel({ decision, threats, evidence }: Props) {
  let tone: Tone = "muted";
  if (decision === "ACCEPT") tone = "success";
  else if (decision === "REJECT") tone = "danger";
  else if (decision === "SUSPICIOUS") tone = "warning";

  return (
    <Card title="Detection decision">
      <div className="flex items-center gap-3">
        <Badge tone={tone}>{decision ?? "n/a"}</Badge>
        {threats && threats.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {threats.map((t) => (
              <Badge key={t} tone="danger">
                {t}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {evidence && evidence.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-xs font-medium text-muted">Evidence</div>
          {evidence.map((e, i) => (
            <pre
              key={i}
              className="overflow-auto rounded-md border border-border bg-bg p-3 text-[11px] font-mono text-muted"
            >
              {JSON.stringify(e, null, 2)}
            </pre>
          ))}
        </div>
      )}
    </Card>
  );
}