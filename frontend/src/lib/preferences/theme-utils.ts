import type { ResolvedThemeMode, ThemeMode, ThemePreset } from "@/lib/preferences/theme";

function getSystemTheme(): ResolvedThemeMode {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyThemeMode(mode: ThemeMode): ResolvedThemeMode {
  const resolved = mode === "system" ? getSystemTheme() : mode;
  const root = document.documentElement;

  root.classList.toggle("dark", resolved === "dark");
  root.setAttribute("data-theme-mode", mode);
  root.style.colorScheme = resolved;

  return resolved;
}

export function subscribeToSystemTheme(callback: () => void) {
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  media.addEventListener("change", callback);
  return () => media.removeEventListener("change", callback);
}

export function applyThemePreset(preset: ThemePreset) {
  document.documentElement.setAttribute("data-theme-preset", preset);
}
