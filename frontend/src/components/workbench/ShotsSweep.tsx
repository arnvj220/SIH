import { useState } from "react";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { api } from "../../lib/api";
import { pct } from "../../lib/format";

interface Row {
  shots: number;
  detection: number;
  fp: number;
  meanError: number;
}

export function ShotsSweep({ attackType }: { attackType: string }) {
  const [rows, setRows] = useState<Row[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setRunning(true);
    setError(null);
    setRows([]);
    const shots = [100, 500, 1000, 5000];
    const out: Row[] = [];
    try {
      for (const s of shots) {
        // Pass no parameters: attack defaults are used. This avoids the
        // "Unsupported parameter" error for attacks like
        // unauthorized_verification that have no numeric sweep param.
        const res = await api.runExperiment({
          attack_type: attackType,
          parameters: {},
          n_targets: 50,
          seed: 12345,
          rounds: s,
          natural_error_rate: 0.01,
        });
        out.push({
          shots: s,
          detection: Number(res.metrics.detection_rate ?? 0),
          fp: Number(res.metrics.false_positive_rate ?? 0),
          meanError: Number(res.metrics.attack_mean_error_rate ?? 0),
        });
        setRows([...out]);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <Card
      title="Shots sweep"
      subtitle="How measurement count affects stability"
      action={
        <Button size="sm" variant="ghost" onClick={run} disabled={running}>
          {running ? "…" : "Run sweep"}
        </Button>
      }
    >
      {error ? (
        <div className="text-xs text-danger">{error}</div>
      ) : rows.length === 0 ? (
        <div className="text-xs text-muted">
          Runs at 100, 500, 1000, 5000 shots per basis.
        </div>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-muted">
              <th className="text-left font-medium">Shots</th>
              <th className="text-right font-medium">Detection</th>
              <th className="text-right font-medium">FP</th>
              <th className="text-right font-medium">Mean err</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.shots} className="border-t border-border">
                <td className="py-1.5 font-mono">{r.shots}</td>
                <td className="py-1.5 text-right font-mono">{pct(r.detection)}</td>
                <td className="py-1.5 text-right font-mono">{pct(r.fp)}</td>
                <td className="py-1.5 text-right font-mono">{pct(r.meanError)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}