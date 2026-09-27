import { NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";
import { ThemeToggle } from "./ThemeToggle";
import { StatusPill } from "./StatusPill";
import { SeedButton } from "./SeedButton";

const NAV = [
  { to: "/", label: "Workbench", end: true },
  { to: "/alerts", label: "Alerts" },
  { to: "/events", label: "Events" },
  { to: "/signatures", label: "Signatures" },
  { to: "/runs", label: "Runs" },
];

export function Shell() {
  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-[1400px] items-center gap-3 px-4 sm:gap-6 sm:px-6">
          <div className="flex shrink-0 items-baseline gap-4">
            <span className="text-base font-semibold text-primary">
              Qureka
            </span>
              <span className="hidden text-xs text-muted md:inline">
              QDS Threat Analysis Workbench
            </span>
          </div>

          <nav className="flex min-w-0 items-center gap-1 overflow-x-auto">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  clsx(
                    "shrink-0 rounded-md px-2 py-1.5 text-sm transition-colors sm:px-3",
                    isActive
                      ? "bg-primary/15 text-primary font-medium"
                      : "text-muted hover:bg-bg hover:text-text"
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex shrink-0 items-center gap-2 sm:gap-3">
            <div className="hidden sm:block">
              <SeedButton />
            </div>
            <StatusPill />
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="flex-1 bg-bg">
        <Outlet />
      </main>

      <footer className="border-t border-border bg-surface">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-3 text-[11px] text-muted">
          <span>Qureka · SIH 2026 · PS 26141</span>
          <span className="font-mono">
            Quantum Digital Signature · Threat Analysis Framework
          </span>
        </div>
      </footer>
    </div>
  );
}