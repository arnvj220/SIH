import { useEffect, useState } from "react";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Empty, Loading } from "../components/ui/Empty";
import { Table } from "../components/ui/Table";
import { DecisionPanel } from "../components/workbench/DecisionPanel";
import { DeviationPanel } from "../components/workbench/DeviationPanel";
import { DistributionChart } from "../components/workbench/DistributionChart";
import { SampleInspector } from "../components/workbench/SampleInspector";
import { api } from "../lib/api";
import { pct, timestamp } from "../lib/format";
import type { ExperimentRunResponse } from "../lib/types";
import { invalidate } from "../lib/cache";
import { Page } from "../components/layout/Page";

interface RunRow {
  run: ExperimentRunResponse;
  attackType: string;
  targets: string;
  rounds: string;
  detectionRate: number;
  falsePositiveRate: number;
}

function toRunRow(run: ExperimentRunResponse): RunRow {
  const config = run.config;
  return {
    run,
    attackType: String(config.attack_type ?? "Unknown"),
    targets: String(config.n_targets ?? "—"),
    rounds: String(config.rounds ?? "—"),
    detectionRate: Number(run.metrics.detection_rate ?? 0),
    falsePositiveRate: Number(run.metrics.false_positive_rate ?? 0),
  };
}

export function Runs() {
  const [runs, setRuns] = useState<ExperimentRunResponse[]>([]);
  const [selected, setSelected] = useState<ExperimentRunResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    invalidate("experiments");
    setLoading(true);
    setError(null);
    try {
      const latestRuns = await api.listExperiments();
      setRuns(latestRuns.slice(0, 10));
      setSelected((current) =>
        current
          ? latestRuns.find((run) => run.experiment_id === current.experiment_id) ?? null
          : null
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

  const rows = runs.map(toRunRow);
  const selectedMetrics = selected?.metrics ?? {};
  const selectedDetection = Number(selectedMetrics.detection_rate ?? 0);
  const selectedPerBasis =
    (selectedMetrics.per_basis as Record<string, number> | undefined) ?? {
      X: 0,
      Y: 0,
      Z: 0,
    };

  return (
    <Page
      title="Runs"
      subtitle="The ten most recent saved experiment runs. Select a run to inspect its results."
      actions={
        <Button size="sm" variant="ghost" onClick={refresh} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </Button>
      }
    >
      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      {loading && runs.length === 0 ? (
        <Loading label="Fetching saved runs..." />
      ) : rows.length === 0 ? (
        <Empty title="No saved runs" hint="Run an experiment from Workbench and it will appear here." />
      ) : (
        <Table<RunRow>
          rows={rows}
          rowKey={(row) => row.run.experiment_id}
          columns={[
            {
              key: "run",
              header: "Run",
              render: (row) => (
                <button
                  className="font-mono text-xs text-primary hover:underline"
                  onClick={() => setSelected(row.run)}
                  aria-label={`Inspect run ${row.run.experiment_id}`}
                >
                  {row.run.experiment_id}
                </button>
              ),
            },
            {
              key: "attack",
              header: "Attack",
              render: (row) => <span className="text-sm text-text">{row.attackType}</span>,
            },
            {
              key: "workload",
              header: "Targets / rounds",
              align: "right",
              render: (row) => <span className="text-xs text-text">{row.targets} / {row.rounds}</span>,
            },
            {
              key: "detection",
              header: "Detection",
              align: "right",
              render: (row) => (
                <Badge tone={row.detectionRate > 0 ? "danger" : "success"}>
                  {pct(row.detectionRate)}
                </Badge>
              ),
            },
            {
              key: "false-positive",
              header: "False positive",
              align: "right",
              render: (row) => <span className="font-mono text-xs text-text">{pct(row.falsePositiveRate)}</span>,
            },
            {
              key: "created",
              header: "Created",
              align: "right",
              render: (row) => <span className="text-xs text-muted">{timestamp(row.run.created_at)}</span>,
            },
          ]}
        />
      )}

      {selected && (
        <section className="mt-6 space-y-6">
          <Card title="Run summary" subtitle={selected.experiment_id}>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <Metric label="Detection" value={pct(selectedDetection)} />
              <Metric label="False positive" value={pct(Number(selectedMetrics.false_positive_rate ?? 0))} />
              <Metric label="Attack mean error" value={pct(Number(selectedMetrics.attack_mean_error_rate ?? 0))} />
              <Metric label="Benign mean error" value={pct(Number(selectedMetrics.benign_mean_error_rate ?? 0))} />
            </div>
          </Card>
          <DistributionChart
            perBasisError={selectedPerBasis}
            overallError={Number(selectedMetrics.attack_mean_error_rate ?? 0)}
            runId={selected.experiment_id}
          />
          <DeviationPanel metrics={selectedMetrics} />
          <SampleInspector attackEvidence={selected.attack_evidence} />
          <DecisionPanel
            decision={selectedDetection > 0 ? "REJECT" : "ACCEPT"}
            threats={selectedDetection > 0 ? [String(selected.config.attack_type ?? "")] : []}
          />
        </section>
      )}
    </Page>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 font-mono text-lg text-text">{value}</div>
    </div>
  );
}
