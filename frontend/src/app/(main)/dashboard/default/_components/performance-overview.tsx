import { BadgeCheck, Brain, CheckCircle2, Database, Route, Wrench } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const agentSteps = [
  {
    title: "意图识别",
    detail: "识别用户目标，例如生成知识卡片、创建自测题或规划复习任务。",
    icon: Brain,
    tag: "Intent",
  },
  {
    title: "任务规划",
    detail: "自动规划资料解析、RAG 检索、知识提取、卡片生成、自测反馈与复习计划。",
    icon: Route,
    tag: "LangGraph",
  },
  {
    title: "工具调用",
    detail: "调用 DocumentParserTool、RAGRetrieverTool、CardGeneratorTool、QuizGeneratorTool 等工具。",
    icon: Wrench,
    tag: "Tools",
  },
  {
    title: "结果校验",
    detail: "检查知识卡片、题目答案、解析和复习建议是否完整。",
    icon: BadgeCheck,
    tag: "Validation",
  },
  {
    title: "记忆更新",
    detail: "保存资料、卡片、答题记录、错题和复习计划，形成长期学习记忆。",
    icon: Database,
    tag: "Memory",
  },
];

export function PerformanceOverview() {
  return (
    <Card className="border-[#e7dffd] bg-[#fffafe]/92 shadow-[0_16px_42px_rgba(109,81,184,0.1)]">
      <CardHeader>
        <CardTitle className="text-[#19162b] leading-none">CardReviewAgent 执行过程</CardTitle>
        <CardDescription className="text-[#6f6680]">
          展示智能体从用户意图到工具调用、记忆更新的完整学习任务链路。
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="grid gap-3 lg:grid-cols-5">
          {agentSteps.map((step, index) => {
            const Icon = step.icon;

            return (
              <div
                key={step.title}
                className="relative rounded-xl border border-[#eadffd] bg-linear-to-b from-[#ffffff] to-[#f7f2ff] p-4 shadow-xs"
              >
                {index < agentSteps.length - 1 && (
                  <div className="absolute top-8 right-[-0.75rem] hidden h-px w-6 bg-[#c5aef1] lg:block" />
                )}
                <div className="mb-4 flex items-center justify-between gap-2">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-[#f0e9ff] text-[#6d51b8]">
                    <Icon className="size-4" />
                  </div>
                  <Badge variant="outline" className="border-[#e2d6fb] text-[#8b5cf6]">
                    {step.tag}
                  </Badge>
                </div>
                <div className="mb-2 flex items-center gap-2">
                  <span className="flex size-5 items-center justify-center rounded-full bg-[#b70f46] font-medium text-[11px] text-white">
                    {index + 1}
                  </span>
                  <h3 className="font-semibold text-[#19162b] text-sm">{step.title}</h3>
                </div>
                <p className="text-[#6f6680] text-sm leading-6">{step.detail}</p>
                <div className="mt-4 flex items-center gap-1.5 text-[#b70f46] text-xs">
                  <CheckCircle2 className="size-3.5" />
                  已纳入学习链路
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
