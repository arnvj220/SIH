import clsx from "clsx";
import type { SelectHTMLAttributes } from "react";

interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: Option[];
}

export function Select({ options, className, ...rest }: SelectProps) {
  return (
    <select
      className={clsx(
        "w-full rounded-md border border-border bg-bg text-text px-3 py-2 text-sm",
        "focus:outline-none focus:border-primary",
        className
      )}
      {...rest}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value} disabled={o.disabled}>
          {o.label}
        </option>
      ))}
    </select>
  );
}