"use client";
"use no memo";

import type { ColumnDef } from "@tanstack/react-table";
import { CheckCircle2, Clock3, FileCheck2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

import type { RecentAgentTaskRow } from "./schema";

function statusBadge(status: string) {
  const running = status === "进行中";

  return (
    <Badge
      variant="outline"
      className={
        running
          ? "border-[#f4b4c9] bg-[#fff6f8] text-[#b70f46]"
          : "border-[#d8cff6] bg-[#f7f2ff] text-[#6d51b8]"
      }
    >
      {running ? <Clock3 className="size-3" /> : <CheckCircle2 className="size-3" />}
      {status}
    </Badge>
  );
}

export const recentAgentTaskColumns: ColumnDef<RecentAgentTaskRow>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <div className="flex items-center justify-center">
        <Checkbox
          checked={table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && "indeterminate")}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="选择当前页全部智能体任务"
        />
      </div>
    ),
    cell: ({ row }) => (
      <div className="flex items-center justify-center">
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label={`选择 ${row.original.taskName}`}
        />
      </div>
    ),
    enableHiding: false,
  },
  {
    accessorKey: "taskName",
    header: "任务名称",
    cell: ({ row }) => (
      <div className="flex min-w-0 items-center gap-2">
        <span className="flex size-8 items-center justify-center rounded-md border border-[#e2d6fb] bg-[#f7f2ff]">
          <FileCheck2 className="size-4 text-[#6d51b8]" />
        </span>
        <div className="grid min-w-0 gap-0.5">
          <span className="truncate font-medium text-[#19162b] text-sm leading-none">{row.original.taskName}</span>
          <span className="truncate text-[#8b7f98] text-xs leading-none">#{row.original.id}</span>
        </div>
      </div>
    ),
    enableHiding: false,
  },
  {
    id: "search",
    accessorFn: (row) => `${row.id} ${row.taskName} ${row.intent} ${row.tools.join(" ")} ${row.status}`,
    filterFn: "includesString",
    enableHiding: true,
  },
  {
    accessorKey: "intent",
    header: "用户意图",
    cell: ({ row }) => <span className="text-sm">{row.original.intent}</span>,
  },
  {
    accessorKey: "tools",
    header: "调用工具",
    cell: ({ row }) => (
      <div className="flex max-w-[360px] flex-wrap gap-1.5">
        {row.original.tools.map((tool) => (
          <Badge key={tool} variant="secondary" className="bg-[#f0e9ff] text-[#6d51b8]">
            {tool}
          </Badge>
        ))}
      </div>
    ),
  },
  {
    accessorKey: "status",
    header: "执行状态",
    filterFn: "equalsString",
    cell: ({ row }) => statusBadge(row.original.status),
  },
  {
    accessorKey: "completedAt",
    header: "完成时间",
    cell: ({ row }) => <span className="text-sm">{row.original.completedAt}</span>,
  },
  {
    accessorKey: "order",
    header: "",
    enableHiding: true,
  },
];
