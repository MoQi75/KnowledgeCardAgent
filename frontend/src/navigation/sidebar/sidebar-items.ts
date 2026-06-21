import {
  BookOpen,
  ChartNoAxesColumnIncreasing,
  ClipboardCheck,
  LayoutDashboard,
  LibraryBig,
  type LucideIcon,
  NotebookPen,
  RotateCcw,
  Settings,
} from "lucide-react";

export type NavBadge = "new" | "soon";

export interface NavSubItem {
  id: string;
  title: string;
  url: string;
  icon?: LucideIcon;
  badge?: NavBadge;
  disabled?: boolean;
  newTab?: boolean;
}

interface NavItemBase {
  id: string;
  title: string;
  icon?: LucideIcon;
  badge?: NavBadge;
  disabled?: boolean;
  newTab?: boolean;
}

export interface NavMainLinkItem extends NavItemBase {
  url: string;
  subItems?: never;
}

export interface NavMainParentItem extends NavItemBase {
  subItems: NavSubItem[];
}

export type NavMainItem = NavMainLinkItem | NavMainParentItem;

export interface NavGroup {
  id: number;
  label?: string;
  items: NavMainItem[];
}

export const sidebarItems: NavGroup[] = [
  {
    id: 1,
    label: "学习工作台",
    items: [
      {
        id: "dashboard",
        title: "仪表盘",
        url: "/dashboard",
        icon: LayoutDashboard,
      },
      {
        id: "documents",
        title: "资料库",
        url: "/dashboard/documents",
        icon: LibraryBig,
      },
      {
        id: "cards",
        title: "知识卡片",
        url: "/dashboard/cards",
        icon: BookOpen,
      },
      {
        id: "quiz",
        title: "自测练习",
        url: "/dashboard/quiz",
        icon: ClipboardCheck,
      },
      {
        id: "wrong-questions",
        title: "错题本",
        url: "/dashboard/wrong-questions",
        icon: NotebookPen,
      },
      {
        id: "review-plan",
        title: "复习计划",
        url: "/dashboard/review-plan",
        icon: RotateCcw,
      },
      {
        id: "stats",
        title: "学习统计",
        url: "/dashboard/stats",
        icon: ChartNoAxesColumnIncreasing,
      },
      {
        id: "settings",
        title: "系统设置",
        url: "/dashboard/settings",
        icon: Settings,
      },
    ],
  },
];
