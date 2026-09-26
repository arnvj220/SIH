import { NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";
import { ThemeToggle } from "./ThemeToggle";

const NAV = [
  { to: "/", label: "Workbench", end: true },
  { to: "/alerts", label: "Alerts" },
  { to: "/events", label: "Events" },
  { to: "/signatures", label: "Signatures" },
];

export function Shell() {
  return (
    <div className="flex h-full">
      <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-surface">
        <div className="border-b border-border px-5 py-5">
          <div className="text-sm font-semibold text-primary">
            QDS THREAT ANALYSIS
          </div>
          <div className="mt-0.5 text-xs text-muted">Workbench v0.1</div>
        </div>

        <nav className="flex-1 px-3 py-4">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                clsx(
                  "block rounded-md px-3 py-2 text-sm transition-colors",
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

        <div className="border-t border-border px-3 py-3">
          <ThemeToggle />
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}