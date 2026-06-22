import { AgentToolbox } from "./_components/agent-toolbox";
import { MetricCards } from "./_components/metric-cards";
import { PerformanceOverview } from "./_components/performance-overview";
import { SubscriberOverview } from "./_components/subscriber-overview";

export default function Page() {
  return (
    <div className="@container/main flex flex-col gap-4 rounded-3xl border border-[#eadffd] bg-[radial-gradient(circle_at_12%_8%,rgba(255,255,255,0.78),transparent_28%),radial-gradient(circle_at_86%_20%,rgba(197,174,241,0.36),transparent_30%),linear-gradient(135deg,#f7f2ff_0%,#eee5ff_52%,#f9eef3_100%)] p-4 shadow-[0_24px_70px_rgba(109,81,184,0.12)] md:gap-6 md:p-6">
      <div className="flex flex-col gap-2">
        <p className="font-medium text-[#b70f46] text-sm">CardReviewAgent</p>
        <div className="max-w-4xl space-y-2">
          <h1 className="font-semibold text-3xl text-[#19162b] tracking-normal">智能体学习仪表盘</h1>
          <p className="text-[#5d5472] text-sm leading-6 md:text-base">
            CardReviewAgent 根据学习资料和答题记录，自动完成资料解析、RAG
            检索、知识卡片生成、自测反馈与复习规划。
          </p>
          <p className="text-[#7b7190] text-xs">
            基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统
          </p>
        </div>
      </div>
      <MetricCards />
      <PerformanceOverview />
      <AgentToolbox />
      <SubscriberOverview />
    </div>
  );
}
