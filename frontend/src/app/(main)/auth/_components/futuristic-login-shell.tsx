import { ArrowRight, BrainCircuit, Network, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { APP_CONFIG } from "@/config/app-config";

import { LoginForm } from "./login-form";

const capabilityTags = ["学习资料智能解析", "知识卡片自动生成", "AI 自测练习", "错题薄弱点分析", "个性化复习计划"];
const flowSteps = ["资料输入", "知识提取", "卡片生成", "自测反馈", "复习规划"];
const floatingCards = ["RAG 检索增强生成", "LangGraph 工作流", "知识卡片", "错题分析", "复习计划"];

export function FuturisticLoginShell() {
  return (
    <main className="relative min-h-dvh overflow-hidden bg-[#060817] text-white">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.35),transparent_32%),radial-gradient(circle_at_78%_16%,rgba(168,85,247,0.32),transparent_30%),radial-gradient(circle_at_50%_90%,rgba(34,211,238,0.2),transparent_34%),linear-gradient(135deg,#050816_0%,#111142_48%,#070a1e_100%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(125,211,252,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(125,211,252,0.08)_1px,transparent_1px)] bg-[size:72px_72px] opacity-45 [mask-image:radial-gradient(circle_at_center,black,transparent_78%)]" />
      <div className="login-aurora pointer-events-none absolute -top-40 left-1/3 h-96 w-96 rounded-full bg-cyan-400/20 blur-3xl" />
      <div className="login-aurora-delayed pointer-events-none absolute right-0 bottom-0 h-[28rem] w-[28rem] rounded-full bg-fuchsia-500/20 blur-3xl" />

      <div className="pointer-events-none absolute inset-0 hidden lg:block">
        {floatingCards.map((item, index) => (
          <div
            className="login-float-card absolute rounded-2xl border border-cyan-300/20 bg-white/[0.06] px-4 py-3 text-cyan-50 text-sm shadow-[0_0_35px_rgba(34,211,238,0.14)] backdrop-blur-xl"
            key={item}
            style={{
              animationDelay: `${index * 0.8}s`,
              left: `${8 + index * 17}%`,
              top: `${13 + (index % 3) * 24}%`,
            }}
          >
            {item}
          </div>
        ))}
      </div>

      <section className="relative z-10 grid min-h-dvh gap-10 px-5 py-8 sm:px-8 lg:grid-cols-[1.15fr_0.85fr] lg:px-12 xl:px-20">
        <div className="flex min-h-[44vh] flex-col justify-center py-8 lg:min-h-0">
          <Badge className="mb-6 w-fit border-cyan-300/30 bg-cyan-300/10 text-cyan-100 hover:bg-cyan-300/10">
            <Sparkles className="mr-1 size-3.5" />
            {APP_CONFIG.shortName}
          </Badge>

          <h1 className="max-w-5xl font-semibold text-3xl leading-tight tracking-normal sm:text-4xl lg:text-5xl xl:text-6xl">
            {APP_CONFIG.name}
          </h1>
          <p className="mt-6 max-w-3xl text-base text-slate-200/82 leading-8 sm:text-lg">
            学习资料解析、知识卡片生成、自测练习、错题分析与复习计划一体化系统
          </p>

          <div className="mt-8 flex max-w-3xl flex-wrap gap-3">
            {capabilityTags.map((tag) => (
              <span
                className="rounded-full border border-white/12 bg-white/[0.07] px-4 py-2 text-slate-100 text-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] backdrop-blur"
                key={tag}
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-10 max-w-4xl rounded-3xl border border-white/10 bg-white/[0.055] p-4 shadow-2xl shadow-blue-950/30 backdrop-blur-xl">
            <div className="mb-4 flex items-center gap-2 text-cyan-100 text-sm">
              <Network className="size-4" />
              智能学习闭环
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {flowSteps.map((step, index) => (
                <div className="flex items-center gap-3" key={step}>
                  <span className="rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-sm text-white">
                    {step}
                  </span>
                  {index < flowSteps.length - 1 && <ArrowRight className="size-4 text-cyan-200/70" />}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-center pb-8 lg:pb-0">
          <div className="login-card-enter relative w-full max-w-md rounded-[2rem] border border-white/18 bg-white/[0.08] p-6 shadow-[0_0_80px_rgba(59,130,246,0.25)] backdrop-blur-2xl sm:p-8">
            <div className="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/80 to-transparent" />
            <div className="mb-8 text-center">
              <div className="mx-auto mb-5 flex size-14 items-center justify-center rounded-2xl border border-cyan-300/30 bg-cyan-300/10 shadow-[0_0_35px_rgba(34,211,238,0.28)]">
                <BrainCircuit className="size-7 text-cyan-100" />
              </div>
              <h2 className="font-semibold text-3xl tracking-normal">欢迎登录</h2>
              <p className="mt-3 text-slate-300 text-sm">进入知识卡片生成与复习规划系统</p>
            </div>

            <LoginForm />

            <p className="mt-7 text-center text-slate-400 text-xs">Powered by LangGraph · FastAPI · RAG</p>
          </div>
        </div>
      </section>
    </main>
  );
}
