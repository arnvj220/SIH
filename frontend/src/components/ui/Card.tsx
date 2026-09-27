import type { HTMLAttributes, ReactNode } from "react";
import clsx from "clsx";


interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  title?: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
  padded?: boolean;
}

export function Card({
  title,
  subtitle,
  action,
  padded = true,
  className,
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={clsx(
        "rounded-lg border border-border bg-surface shadow-sm shadow-black/5",
        className
      )}
      {...rest}
    >
      {(title || action) && (
        <div className="flex items-start justify-between gap-4 border-b border-border px-4 py-3">
          <div className="min-w-0">
            {title && (
              <div className="text-sm font-semibold text-text truncate">
                {title}
              </div>
            )}
            {subtitle && (
              <div className="mt-0.5 text-xs text-muted truncate">
                {subtitle}
              </div>
            )}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className={clsx(padded && "p-4")}>{children}</div>
    </div>
  );
}