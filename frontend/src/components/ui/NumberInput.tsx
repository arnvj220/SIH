import type { ChangeEvent } from "react";

interface NumberInputProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (v: number) => void;
}

export function NumberInput({
  label,
  value,
  min,
  max,
  step = 1,
  onChange,
}: NumberInputProps) {
  const handle = (e: ChangeEvent<HTMLInputElement>) => {
    const n = Number(e.target.value);
    if (!Number.isNaN(n)) onChange(n);
  };

  return (
    <label className="block">
      <span className="text-xs font-medium text-muted">{label}</span>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={handle}
        className="mt-1 w-full rounded-md border border-border bg-bg text-text px-3 py-2 text-sm font-mono focus:outline-none focus:border-primary"
      />
    </label>
  );
}