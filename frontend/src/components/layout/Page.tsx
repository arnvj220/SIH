import type { ReactNode } from "react";
import { PageHeader } from "./PageHeader";

interface Props {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  /** Apply the workbench grid pattern behind this page. */
  grid?: boolean;
}

export function Page({
  title,
  subtitle,
  actions,
  children,
  grid = false,
}: Props) {
  return (
    <div className={grid ? "workbench-grid min-h-full" : "min-h-full"}>
      <div className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 sm:py-8">
        <PageHeader title={title} subtitle={subtitle} actions={actions} />
        {children}
      </div>
    </div>
  );
}