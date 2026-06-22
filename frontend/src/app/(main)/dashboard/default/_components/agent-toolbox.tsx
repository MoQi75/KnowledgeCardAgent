import { BookOpenCheck, BrainCircuit, CheckCircle2, Database, FileText, Search, Target, Wrench } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const tools = [
  { name: "DocumentParserTool", role: "资料解析", icon: FileText },
  { name: "RAGRetrieverTool", role: "RAG 检索", icon: Search },
  { name: "CardGeneratorTool", role: "知识卡片生成", icon: BookOpenCheck },
  { name: "QuizGeneratorTool", role: "自测题生成", icon: BrainCircuit },
  { name: "AnswerCheckerTool", role: "答案批改", icon: CheckCircle2 },
  { name: "WeaknessAnalyzerTool", role: "薄弱点分析", icon: Target },
  { name: "ReviewPlannerTool", role: "复习计划生成", icon: Wrench },
  { name: "MemoryTool", role: "学习记忆更新", icon: Database },
];

export function AgentToolbox() {
  return (
    <Card className="border-[#e7dffd] bg-[#fffafe]/92 shadow-[0_16px_42px_rgba(109,81,184,0.1)]">
      <CardHeader>
        <CardTitle className="text-[#19162b] leading-none">智能体工具箱</CardTitle>
        <CardDescription className="text-[#6f6680]">
          CardReviewAgent 在学习任务中按需编排以下工具。
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {tools.map((tool) => {
            const Icon = tool.icon;

            return (
              <div
                key={tool.name}
                className="rounded-xl border border-[#eadffd] bg-linear-to-b from-[#ffffff] to-[#f7f2ff] p-4"
              >
                <div className="mb-3 flex size-9 items-center justify-center rounded-xl bg-[#f0e9ff] text-[#6d51b8]">
                  <Icon className="size-4" />
                </div>
                <div className="font-semibold text-[#19162b] text-sm">{tool.name}</div>
                <div className="mt-1 text-[#6f6680] text-sm">{tool.role}</div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
