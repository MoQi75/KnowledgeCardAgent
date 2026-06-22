export const CONTENT_LAYOUT_VALUES = ["centered", "full-width"] as const;
export type ContentLayout = (typeof CONTENT_LAYOUT_VALUES)[number];

export const NAVBAR_STYLE_VALUES = ["sticky", "scroll"] as const;
export type NavbarStyle = (typeof NAVBAR_STYLE_VALUES)[number];

export const SIDEBAR_VARIANT_VALUES = ["inset", "sidebar", "floating"] as const;
export type SidebarVariant = (typeof SIDEBAR_VARIANT_VALUES)[number];

export const SIDEBAR_COLLAPSIBLE_VALUES = ["icon", "offcanvas"] as const;
export type SidebarCollapsible = (typeof SIDEBAR_COLLAPSIBLE_VALUES)[number];
