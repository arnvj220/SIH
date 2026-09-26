import { Card } from "../ui/Card";
import { pct } from "../../lib/format";

interface Props {
  metrics: Record<string, unknown>;
}

const METRIC_LABELS: Record<string, string> = {
  detection_rate: "Detection rate",
  false_positive_rate: "False positive rate",
  false_negative_rate: "False negative rate",
  classification_rate: "Classification rate",
  exact_classification_rate: "Exact classification rate",
  attack_mean_error_rate: "Attack mean error rate",
  benign_mean_error_rate: "Benign mean error rate",
  latency_mean_ms: "Mean latency (ms)",
  latency_p95_ms: "P95 latency (ms)",
  throughput_per_s: "Throughput / s",
};

export function DeviationPanel({ metrics }: Props) {
  return (
    <Card title="Statistical metrics" subtitle="Derived from the run">
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        {Object.entries(METRIC_LABELS).map(([key, label]) => {
          const v = metrics[key];
          if (v === undefined || v === null) return null;
          const isRate = key.endsWith("_rate");
          return (
            <div key={key} className="flex items-baseline justify-between">
              <dt className="text-xs text-muted">{label}</dt>
              <dd className="font-mono text-text">
                {isRate ? pct(v as number) : String(v)}
              </dd>
            </div>
          );
        })}
      </dl>
    </Card>
  );
}