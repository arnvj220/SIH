import clsx from "clsx";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-md font-medium",
        "transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary",
        size === "sm" ? "px-2.5 py-1 text-xs" : "px-3.5 py-2 text-sm",
        variant === "primary" &&
          "bg-primary text-white hover:opacity-90 active:opacity-80",
        variant === "secondary" &&
          "bg-secondary text-white hover:opacity-90 active:opacity-80",
        variant === "ghost" &&
          "bg-transparent text-text border border-border hover:bg-bg",
        variant === "danger" &&
          "bg-danger text-white hover:opacity-90 active:opacity-80",
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
}