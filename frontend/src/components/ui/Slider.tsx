import type { ChangeEvent } from "react";

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  format?: (v: number) => string;
}

export function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  format = (v) => v.toFixed(2),
}: SliderProps) {
  const handle = (e: ChangeEvent<HTMLInputElement>) =>
    onChange(Number(e.target.value));

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <label className="text-xs font-medium text-muted">{label}</label>
        <span className="text-xs font-mono text-text">{format(value)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={handle}
        className="mt-2 w-full accent-primary"
      />
    </div>
  );
}