import { BookOpenCheck, BrainCircuit, ClipboardCheck, FileText, Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const metrics = [
  {
    title: "今日解析资料",
    value: "12 份",
    description: "智能体已完成资料解析与切片",
    icon: FileText,
    badge: "DocumentParserTool",
  },
  {
    title: "已生成知识卡片",
    value: "86 张",
    description: "覆盖核心概念、示例和易错点",
    icon: BookOpenCheck,
    badge: "CardGeneratorTool",
  },
  {
    title: "自测完成次数",
    value: "34 次",
    description: "根据知识卡片自动生成练习",
    icon: ClipboardCheck,
    badge: "QuizGeneratorTool",
  },
  {
    title: "待复习薄弱点",
    value: "7 个",
    description: "由错题记录和掌握度分析得出",
    icon: Target,
    badge: "WeaknessAnalyzerTool",
  },
];

export function MetricCards() {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-4">
      {metrics.map((metric) => {
        const Icon = metric.icon;

        return (
          <Card
            key={metric.title}
            className="border-[#e7dffd] bg-linear-to-t from-[#f0e9ff] to-[#fffafe] shadow-[0_12px_32px_rgba(109,81,184,0.1)]"
          >
            <CardHeader>
              <CardTitle>
                <div className="flex size-8 items-center justify-center rounded-lg border border-[#e2d6fb] bg-[#f7f2ff] text-[#6d51b8]">
                  <Icon className="size-4" />
                </div>
              </CardTitle>
              <CardDescription className="text-[#5d5472]">{metric.title}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <div className="font-medium text-3xl text-[#19162b] tabular-nums leading-none tracking-tight">
                  {metric.value}
                </div>
                <Badge className="bg-[#b70f46] text-white hover:bg-[#b70f46]">
                  <BrainCircuit className="size-3" />
                  Agent
                </Badge>
              </div>
              <p className="text-[#6f6680] text-sm">{metric.description}</p>
              <p className="text-[#8b5cf6] text-xs">{metric.badge}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
