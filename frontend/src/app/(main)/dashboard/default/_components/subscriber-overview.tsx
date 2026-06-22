"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import agentTasksData from "./data.json";
import type { RecentAgentTaskRow } from "./recent-customers-table/schema";
import { RecentAgentTasksTable } from "./recent-customers-table/table";

const agentTasks = agentTasksData as RecentAgentTaskRow[];

export function SubscriberOverview() {
  return (
    <Card className="border-[#e7dffd] bg-[#fffafe]/92 shadow-[0_16px_42px_rgba(109,81,184,0.1)]">
      <CardHeader>
        <CardTitle className="text-[#19162b] leading-none">最近智能体任务</CardTitle>
        <CardDescription className="text-[#6f6680]">
          记录 CardReviewAgent 最近执行的学习任务、调用工具和处理状态。
        </CardDescription>
        <CardAction>
          <Button variant="outline" size="sm">
            <Download />
            导出记录
          </Button>
        </CardAction>
      </CardHeader>

      <CardContent className="pt-0">
        <RecentAgentTasksTable data={agentTasks} />
      </CardContent>
    </Card>
  );
}
