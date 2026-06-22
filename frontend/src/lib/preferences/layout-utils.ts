import type { FontKey } from "@/lib/fonts/registry";
import type { ContentLayout, NavbarStyle, SidebarCollapsible, SidebarVariant } from "@/lib/preferences/layout";

function root() {
  return document.documentElement;
}

export function applyContentLayout(value: ContentLayout) {
  root().setAttribute("data-content-layout", value);
}

export function applyNavbarStyle(value: NavbarStyle) {
  root().setAttribute("data-navbar-style", value);
}

export function applySidebarVariant(value: SidebarVariant) {
  root().setAttribute("data-sidebar-variant", value);
}

export function applySidebarCollapsible(value: SidebarCollapsible) {
  root().setAttribute("data-sidebar-collapsible", value);
}

export function applyFont(value: FontKey) {
  root().setAttribute("data-font", value);
}
