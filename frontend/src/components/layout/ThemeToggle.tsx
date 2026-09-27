import { useTheme } from "../../theme/ThemeProvider";

export function ThemeToggle() {
  const { mode, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      title={`Switch to ${mode === "dark" ? "light" : "dark"} mode`}
      className="flex items-center gap-1.5 rounded-md border border-border bg-bg px-2.5 py-1 text-[11px] text-muted hover:text-text"
    >
      <span aria-hidden>{mode === "dark" ? "☾" : "☀"}</span>
      <span>{mode === "dark" ? "Eclipse" : "Ivory"}</span>
    </button>
  );
}