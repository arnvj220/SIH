import { useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTheme } from "../../theme/ThemeProvider";
import { api } from "../../lib/api";
import { sweepKeyFor } from "../../lib/attackParams";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import type { AttackDescription } from "../../lib/types";

interface Point {
  strength: number;
  detection: number;
}

export function ParameterSweep({
  attackType,
  attacks,
}: {
  attackType: string;
  attacks: AttackDescription[];
}) {
  const { palette } = useTheme();
  const [points, setPoints] = useState<Point[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const attack = attacks.find((a) => a.name === attackType);
  const sweepKey = sweepKeyFor(attack);

  const run = async () => {
    if (!sweepKey) return;
    setRunning(true);
    setError(null);
    setPoints([]);
    const strengths = [0.05, 0.1, 0.2, 0.3];
    const results: Point[] = [];
    try {
      for (const s of strengths) {
        const res = await api.runExperiment({
          attack_type: attackType,
          parameters: { [sweepKey]: s },
          n_targets: 50,
          seed: 12345,
          rounds: 100,
          natural_error_rate: 0.01,
        });
        const rate = Number(res.metrics.detection_rate ?? 0);
        results.push({ strength: s, detection: rate });
        setPoints([...results]);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <Card
      title={sweepKey ? `Parameter sweep · ${sweepKey}` : "Parameter sweep"}
      subtitle="Attack strength → detection rate"
      action={
        <Button
          size="sm"
          variant="ghost"
          onClick={run}
          disabled={running || !sweepKey}
        >
          {running ? "…" : "Run sweep"}
        </Button>
      }
    >
      {!sweepKey ? (
        <div className="text-xs text-muted">
          {attackType} has no continuous strength parameter to sweep.
        </div>
      ) : error ? (
        <div className="text-xs text-danger">{error}</div>
      ) : points.length === 0 ? (
        <div className="text-xs text-muted">
          Runs the attack at {sweepKey} = 5%, 10%, 20%, 30%.
        </div>
      ) : (
        <div className="h-48 sm:h-56">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid stroke={palette.border} strokeDasharray="3 3" />
              <XAxis
                dataKey="strength"
                stroke={palette.muted}
                tick={{ fill: palette.muted, fontSize: 12 }}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              />
              <YAxis
                stroke={palette.muted}
                tick={{ fill: palette.muted, fontSize: 12 }}
                domain={[0, 1]}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              />
              <Tooltip
                contentStyle={{
                  background: palette.surface,
                  border: `1px solid ${palette.border}`,
                  borderRadius: 8,
                  fontSize: 12,
                  color: palette.text,
                }}
                formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
              />
              <Line
  type="monotone"
  dataKey="detection"
  stroke={palette.accent}
  strokeWidth={2}
  dot={{ r: 4, fill: palette.accent }}
  isAnimationActive={true}
  animationDuration={500}
  animationEasing="ease-out"
/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}