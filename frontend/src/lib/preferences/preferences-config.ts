import type { FontKey } from "@/lib/fonts/registry";
import type { ContentLayout, NavbarStyle, SidebarCollapsible, SidebarVariant } from "@/lib/preferences/layout";
import type { ThemeMode, ThemePreset } from "@/lib/preferences/theme";

export type PreferenceKey =
  | "theme_mode"
  | "theme_preset"
  | "font"
  | "content_layout"
  | "navbar_style"
  | "sidebar_variant"
  | "sidebar_collapsible";

export type PreferencePersistence = "localStorage" | "client-cookie" | "server-cookie";

export const PREFERENCE_DEFAULTS: Record<PreferenceKey, string> & {
  theme_mode: ThemeMode;
  theme_preset: ThemePreset;
  font: FontKey;
  content_layout: ContentLayout;
  navbar_style: NavbarStyle;
  sidebar_variant: SidebarVariant;
  sidebar_collapsible: SidebarCollapsible;
} = {
  theme_mode: "light",
  theme_preset: "default",
  font: "geist",
  content_layout: "centered",
  navbar_style: "sticky",
  sidebar_variant: "inset",
  sidebar_collapsible: "icon",
};

export const PREFERENCE_PERSISTENCE: Record<PreferenceKey, PreferencePersistence> = {
  theme_mode: "client-cookie",
  theme_preset: "client-cookie",
  font: "client-cookie",
  content_layout: "client-cookie",
  navbar_style: "client-cookie",
  sidebar_variant: "client-cookie",
  sidebar_collapsible: "client-cookie",
};
