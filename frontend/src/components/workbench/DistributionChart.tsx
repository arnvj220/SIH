import { useEffect, useRef, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTheme } from "../../theme/ThemeProvider";
import { Card } from "../ui/Card";

interface Props {
  perBasisError: Record<string, number>;
  overallError: number;
  runId?: string;
}

interface Row {
  basis: string;
  error: number;
  agreement: number;
  prevError: number | null;
}

export function DistributionChart({ perBasisError, overallError, runId }: Props) {
  const { palette } = useTheme();
  const prevRef = useRef<Record<string, number> | null>(null);
  const [rows, setRows] = useState<Row[]>([]);

  useEffect(() => {
    const prev = prevRef.current;
    const next: Row[] = ["X", "Y", "Z"].map((b) => {
      const err = perBasisError[b] ?? 0;
      return {
        basis: b,
        error: err,
        agreement: 1 - err,
        prevError: prev?.[b] ?? null,
      };
    });
    setRows(next);
    // Store current as previous for the next render.
    prevRef.current = { ...perBasisError };
  }, [perBasisError, runId]);

  return (
    <Card
      title="Per-basis error distribution"
      subtitle={`Overall error rate: ${(overallError * 100).toFixed(2)}%`}
    >
      <div className="h-56 sm:h-64 md:h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={palette.border} strokeDasharray="3 3" />
            <XAxis
              dataKey="basis"
              stroke={palette.muted}
              tick={{ fill: palette.muted, fontSize: 12 }}
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
              formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: palette.muted }} />
            <Bar
              dataKey="prevError"
              name="Previous run"
              fill={palette.muted}
              fillOpacity={0.25}
              radius={[4, 4, 0, 0]}
              isAnimationActive={true}
              animationDuration={400}
            />
            <Bar
              dataKey="error"
              name="Error rate"
              fill={palette.primary}
              radius={[4, 4, 0, 0]}
              isAnimationActive={true}
              animationDuration={600}
              animationEasing="ease-out"
            />
            <Bar
              dataKey="agreement"
              name="Agreement"
              fill={palette.secondary}
              fillOpacity={0.7}
              radius={[4, 4, 0, 0]}
              isAnimationActive={true}
              animationDuration={600}
              animationEasing="ease-out"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}