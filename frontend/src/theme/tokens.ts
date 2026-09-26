/**
 * Palette for use in JS contexts (Recharts, canvas, inline style).
 * Mirrors the CSS variables in index.css.
 */

export type ThemeMode = "dark" | "light";

export interface Palette {
  bg: string;
  surface: string;
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  muted: string;
  border: string;
  success: string;
  warning: string;
  danger: string;
}

export const DARK: Palette = {
  bg: "#090817",
  surface: "#15112A",
  primary: "#D946EF",
  secondary: "#38BDF8",
  accent: "#A3E635",
  text: "#F5F3FF",
  muted: "#A5A0B8",
  border: "#30284A",
  success: "#3FA66B",
  warning: "#D99125",
  danger: "#C94A4A",
};

export const LIGHT: Palette = {
  bg: "#F6F1E8",
  surface: "#FFFDF7",
  primary: "#B4238A",
  secondary: "#176B87",
  accent: "#6B7A20",
  text: "#211A2E",
  muted: "#756D7D",
  border: "#D8CEDC",
  success: "#3FA66B",
  warning: "#D99125",
  danger: "#C94A4A",
};

export function paletteFor(mode: ThemeMode): Palette {
  return mode === "dark" ? DARK : LIGHT;
}