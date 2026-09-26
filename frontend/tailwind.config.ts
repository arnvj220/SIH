import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Semantic tokens driven by CSS variables so both themes work
        // without duplicating every class with dark: prefixes.
        bg:        "rgb(var(--color-bg) / <alpha-value>)",
        surface:   "rgb(var(--color-surface) / <alpha-value>)",
        primary:   "rgb(var(--color-primary) / <alpha-value>)",
        secondary: "rgb(var(--color-secondary) / <alpha-value>)",
        accent:    "rgb(var(--color-accent) / <alpha-value>)",
        text:      "rgb(var(--color-text) / <alpha-value>)",
        muted:     "rgb(var(--color-muted) / <alpha-value>)",
        border:    "rgb(var(--color-border) / <alpha-value>)",
        success:   "rgb(var(--color-success) / <alpha-value>)",
        warning:   "rgb(var(--color-warning) / <alpha-value>)",
        danger:    "rgb(var(--color-danger) / <alpha-value>)",
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
