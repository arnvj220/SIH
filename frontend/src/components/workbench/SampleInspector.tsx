import { useState } from "react";
import { Card } from "../ui/Card";
import { Table } from "../ui/Table";
import { num } from "../../lib/format";

interface EvidenceRow {
  rule_id?: string;
  metric?: string;
  observed?: unknown;
  threshold?: unknown;
  explanation?: string;
  type?: string;
}

interface Props {
  attackEvidence: Record<string, unknown>;
}

function extractRows(attackEvidence: Record<string, unknown>): EvidenceRow[] {
  const rows: EvidenceRow[] = [];

  // attack_evidence has shape { attack, seed, parameters, ...counters }
  // Pull the summary parts most useful for the researcher.
  if (typeof attackEvidence.attack === "string") {
    rows.push({
      rule_id: "attack.scenario",
      metric: "attack",
      observed: attackEvidence.attack,
      threshold: "—",
      explanation: "Scenario name that produced this run.",
    });
  }
  if (typeof attackEvidence.seed === "number") {
    rows.push({
      rule_id: "attack.seed",
      metric: "seed",
      observed: attackEvidence.seed,
      threshold: "—",
      explanation: "RNG seed used — same seed → same run.",
    });
  }
  if (attackEvidence.parameters && typeof attackEvidence.parameters === "object") {
    for (const [k, v] of Object.entries(
      attackEvidence.parameters as Record<string, unknown>
    )) {
      rows.push({
        rule_id: `attack.param.${k}`,
        metric: k,
        observed: v,
        threshold: "—",
        explanation: "Attack parameter as configured.",
      });
    }
  }
  if (typeof attackEvidence.contexts_generated === "number") {
    rows.push({
      rule_id: "attack.contexts_generated",
      metric: "contexts_generated",
      observed: attackEvidence.contexts_generated,
      threshold: "—",
      explanation: "Number of attacked contexts produced.",
    });
  }
  // Include per-basis info if present
  const perBasis = attackEvidence.per_basis;
  if (perBasis && typeof perBasis === "object") {
    for (const [basis, stats] of Object.entries(
      perBasis as Record<string, unknown>
    )) {
      if (stats && typeof stats === "object") {
        const s = stats as Record<string, unknown>;
        rows.push({
          rule_id: `per_basis.${basis}.error_rate`,
          metric: `error_rate[${basis}]`,
          observed: s.error_rate,
          threshold: "—",
          explanation: `Observed error rate for ${basis} basis.`,
        });
      }
    }
  }
  return rows;
}

export function SampleInspector({ attackEvidence }: Props) {
  const [open, setOpen] = useState(false);
  const rows = extractRows(attackEvidence);

  return (
    <Card
      title="Attack evidence"
      subtitle="What this run did — inspect, don't trust"
      action={
        <button
          onClick={() => setOpen((o) => !o)}
          className="text-xs text-muted hover:text-text"
        >
          {open ? "Hide raw JSON" : "Show raw JSON"}
        </button>
      }
    >
      <Table<EvidenceRow>
        rows={rows}
        rowKey={(r, i) => `${r.rule_id ?? "row"}-${i}`}
        empty="No evidence recorded for this run."
        columns={[
          {
            key: "rule",
            header: "Rule / key",
            render: (r) => (
              <span className="font-mono text-[11px] text-primary">
                {r.rule_id ?? "—"}
              </span>
            ),
          },
          {
            key: "metric",
            header: "Metric",
            render: (r) => (
              <span className="font-mono text-xs text-text">{r.metric}</span>
            ),
          },
          {
            key: "observed",
            header: "Observed",
            align: "right",
            render: (r) => (
              <span className="font-mono text-xs text-text">
                {typeof r.observed === "number" ? num(r.observed) : String(r.observed ?? "—")}
              </span>
            ),
          },
          {
            key: "threshold",
            header: "Threshold",
            align: "right",
            render: (r) => (
              <span className="font-mono text-xs text-muted">
                {typeof r.threshold === "number" ? num(r.threshold) : String(r.threshold ?? "—")}
              </span>
            ),
          },
          {
            key: "explanation",
            header: "Explanation",
            render: (r) => (
              <span className="text-xs text-muted">{r.explanation ?? "—"}</span>
            ),
          },
        ]}
      />

      {open && (
        <pre className="mt-4 max-h-72 overflow-auto rounded-md border border-border bg-bg p-3 text-[11px] font-mono text-muted">
          {JSON.stringify(attackEvidence, null, 2)}
        </pre>
      )}
    </Card>
  );
}