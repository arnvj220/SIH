import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card";
import { Empty } from "../components/ui/Empty";
import { Badge } from "../components/ui/Badge";
import { ExperimentConfig } from "../components/workbench/ExperimentConfig";
import { DistributionChart } from "../components/workbench/DistributionChart";
import { DeviationPanel } from "../components/workbench/DeviationPanel";
import { DecisionPanel } from "../components/workbench/DecisionPanel";
import { ParameterSweep } from "../components/workbench/ParameterSweep";
import { ShotsSweep } from "../components/workbench/ShotsSweep";
import { api } from "../lib/api";
import { pct } from "../lib/format";
import type {
  AttackDescription,
  ExperimentRunRequest,
  ExperimentRunResponse,
} from "../lib/types";
import { sanitizeParamsForAttack } from "../lib/attackParams";
import { SampleInspector } from "../components/workbench/SampleInspector";
import { Page } from "../components/layout/Page";

const DEFAULT_REQUEST: ExperimentRunRequest = {
  attack_type: "channel_manipulation",
  parameters: { mode: "depolarizing", perturbation: 0.2 },
  n_targets: 100,
  seed: 12345,
  rounds: 100,
  natural_error_rate: 0.01,
};

export function Workbench() {
  const [attacks, setAttacks] = useState<AttackDescription[]>([]);
  const [req, setReq] = useState<ExperimentRunRequest>(DEFAULT_REQUEST);
  const [result, setResult] = useState<ExperimentRunResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    api
      .listAttacks()
      .then((availableAttacks) => {
        if (!cancelled) setAttacks(availableAttacks);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const runExperiment = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await api.runExperiment({
        ...req,
        parameters: sanitizeParamsForAttack(attacks, req.attack_type, req.parameters),
      });
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  };

  const metrics = result?.metrics ?? {};
  const detectionRate = Number(metrics.detection_rate ?? 0);
  const falsePositive = Number(metrics.false_positive_rate ?? 0);
  const attackMean = Number(metrics.attack_mean_error_rate ?? 0);
  const benignMean = Number(metrics.benign_mean_error_rate ?? 0);
  const perBasis = (metrics.per_basis as Record<string, number> | undefined) ?? {
    X: 0,
    Y: 0,
    Z: 0,
  };

  return (
    <Page
      title="Workbench"
      subtitle="Configure, run, and inspect a QDS attack experiment against the real detection engine."
      grid
    >
      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="space-y-6">
          <ExperimentConfig
            attacks={attacks}
            value={req}
            onChange={setReq}
            onRun={runExperiment}
            running={running}
          />
        </aside>

        <section className="space-y-6">
          {!result ? (
            <Empty
              title="No run yet"
              hint="Configure the experiment on the left and press Run Experiment."
            />
          ) : (
            <>
              <Card title="Run summary" subtitle={result.experiment_id}>
                <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
                  <Stat label="Detection" value={pct(detectionRate)} tone="success" />
                  <Stat label="False positive" value={pct(falsePositive)} tone="warning" />
                  <Stat label="Attack mean err" value={pct(attackMean)} />
                  <Stat label="Benign mean err" value={pct(benignMean)} />
                </div>
              </Card>

              <DistributionChart
                perBasisError={perBasis}
                overallError={attackMean}
                runId={result.experiment_id}
              />
              <DeviationPanel metrics={metrics} />
              <SampleInspector
                attackEvidence={result.attack_evidence}
              />
              <DecisionPanel
                decision={detectionRate > 0 ? "REJECT" : "ACCEPT"}
                threats={
                  detectionRate > 0
                    ? [(result.config as { attack_type?: string }).attack_type ?? ""].filter(Boolean)
                    : []
                }
              />
            </>
          )}

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <ParameterSweep attackType={req.attack_type} attacks={attacks} />
            <ShotsSweep attackType={req.attack_type} />
          </div>
        </section>
      </div>
    </Page>
  );
}

function Stat({
  label,
  value,
  tone = "muted",
}: {
  label: string;
  value: string;
  tone?: "success" | "warning" | "danger" | "muted";
}) {
  return (
    <div>
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="font-mono text-lg text-text">{value}</span>
        <Badge tone={tone}>{tone.toUpperCase()}</Badge>
      </div>
    </div>
  );
}