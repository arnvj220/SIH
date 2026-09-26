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
  /** Per-basis error rates from the run: { X: 0.02, Y: 0.04, Z: 0.08 } */
  perBasisError: Record<string, number>;
  overallError: number;
}

export function DistributionChart({ perBasisError, overallError }: Props) {
  const { palette } = useTheme();

  const data = ["X", "Y", "Z"].map((b) => ({
    basis: b,
    error: perBasisError[b] ?? 0,
    clean: 1 - (perBasisError[b] ?? 0),
  }));

  return (
    <Card
      title="Per-basis error distribution"
      subtitle={`Overall error rate: ${(overallError * 100).toFixed(2)}%`}
    >
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
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
            <Bar dataKey="error" fill={palette.primary} name="Error rate" radius={[4, 4, 0, 0]} />
            <Bar dataKey="clean" fill={palette.secondary} name="Agreement" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}