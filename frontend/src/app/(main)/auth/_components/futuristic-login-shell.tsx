import { ArrowRight, BookOpenCheck, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { APP_CONFIG } from "@/config/app-config";

import { LoginForm } from "./login-form";

const formalProjectName = "基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统";
const capabilityTags = ["资料智能解析", "知识卡片生成", "AI 自测练习", "错题分析", "复习计划"];
const flowSteps = ["资料输入", "知识提取", "卡片生成", "自测反馈", "复习规划"];
const floatingCards = ["RAG", "LangGraph", "知识卡片", "自测练习", "错题分析", "复习计划"];

export function FuturisticLoginShell() {
  return (
    <main className="relative min-h-dvh overflow-hidden bg-[#e4dff5] text-[#12121c]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(255,255,255,0.82),transparent_26%),radial-gradient(circle_at_86%_12%,rgba(197,174,241,0.56),transparent_30%),radial-gradient(circle_at_70%_88%,rgba(255,226,236,0.78),transparent_28%),linear-gradient(135deg,#f7f1ff_0%,#e4dff5_45%,#f8e8ee_100%)]" />
      <div className="login-soft-orb pointer-events-none absolute top-20 -left-20 h-64 w-64 rounded-full bg-[#c5aef1]/45 blur-2xl" />
      <div className="login-soft-orb-delayed pointer-events-none absolute right-12 bottom-8 h-80 w-80 rounded-full bg-[#ffc5d4]/45 blur-2xl" />

      <section className="relative z-10 grid min-h-dvh gap-6 px-5 py-5 sm:px-8 lg:grid-cols-[0.42fr_0.58fr] lg:px-10 xl:px-16">
        <div className="login-panel-enter flex min-h-[calc(100dvh-2.5rem)] flex-col justify-center">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-2xl bg-[#9d0633] text-white shadow-[0_14px_28px_rgba(157,6,51,0.22)]">
              <BookOpenCheck className="size-5" />
            </div>
            <div>
              <div className="font-semibold text-lg">{APP_CONFIG.name}</div>
              <div className="text-[#5d5472] text-xs">{APP_CONFIG.shortName}</div>
            </div>
          </div>

          <div className="rounded-[2rem] bg-white/82 p-6 shadow-[0_24px_70px_rgba(78,55,126,0.18)] backdrop-blur-xl sm:p-8 xl:p-10">
            <div className="mb-8">
              <Badge className="mb-4 border-[#c5aef1]/50 bg-[#f0e9ff] text-[#6d51b8] hover:bg-[#f0e9ff]">
                <Sparkles className="mr-1 size-3.5" />
                智能学习入口
              </Badge>
              <h1 className="font-semibold text-3xl text-[#12121c] tracking-normal">欢迎登录</h1>
              <p className="mt-3 text-[#6f6680] text-sm">进入知识卡片生成与复习规划系统</p>
            </div>

            <LoginForm />

            <p className="mt-7 text-center text-[#857a98] text-xs">Powered by LangGraph · FastAPI · RAG</p>
          </div>
        </div>

        <div className="login-illustration-enter hidden min-h-[calc(100dvh-2.5rem)] flex-col justify-center lg:flex">
          <div className="relative overflow-hidden rounded-[2.5rem] bg-white/34 p-8 shadow-[0_28px_80px_rgba(109,81,184,0.2)] backdrop-blur-md xl:p-12">
            <div className="absolute -top-10 -right-12 h-44 w-44 rounded-full bg-[#c5aef1]" />
            <div className="absolute top-12 right-28 h-24 w-56 rounded-full bg-[#fff4f7]" />
            <div className="absolute -bottom-16 left-10 h-48 w-48 rounded-full bg-[#ae99f1]/45" />

            <div className="relative z-10 max-w-3xl">
              <div className="mb-5 inline-flex rounded-full bg-white/65 px-4 py-2 font-medium text-[#6d51b8] text-sm shadow-sm">
                {APP_CONFIG.shortName}
              </div>
              <h2
                aria-label={formalProjectName}
                className="max-w-4xl font-semibold text-4xl text-[#12121c] leading-tight tracking-normal xl:text-5xl"
              >
                基于 LangGraph + FastAPI + RAG 的
                <span className="block">知识卡片生成与复习规划智能体系统</span>
              </h2>
              <p className="mt-5 max-w-2xl text-[#5d5472] leading-8">
                上传学习资料，生成知识卡片，完成自测练习，分析薄弱知识点，规划个性化复习路径。
              </p>

              <div className="mt-6 flex flex-wrap gap-2">
                {capabilityTags.map((tag) => (
                  <span className="rounded-full bg-white/72 px-4 py-2 text-[#4f4564] text-sm shadow-sm" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="relative z-10 mt-8 min-h-[330px] xl:min-h-[390px]">
              <div className="absolute top-14 left-8 h-44 w-44 rounded-full bg-[#c5aef1]/70" />
              <div className="absolute top-6 left-32 h-20 w-40 rounded-full bg-[#f7d5df]" />
              <div className="absolute right-16 bottom-14 h-28 w-64 rounded-full bg-[#d8cff6]" />

              <svg
                aria-label="学生在知识卡片空间中学习的插画"
                className="login-illustration-float absolute top-4 left-12 h-[310px] w-[360px] xl:h-[360px] xl:w-[420px]"
                role="img"
                viewBox="0 0 420 360"
              >
                <title>学生在知识卡片空间中学习</title>
                <path d="M52 284c34-50 96-72 164-64 63 7 112 39 151 84H52z" fill="#D8CFF6" />
                <rect x="105" y="210" width="205" height="38" rx="19" fill="#9D0633" opacity=".88" />
                <rect x="118" y="125" width="156" height="112" rx="24" fill="#fff" />
                <rect x="135" y="144" width="96" height="12" rx="6" fill="#C5AEF1" />
                <rect x="135" y="166" width="116" height="10" rx="5" fill="#E9E0FA" />
                <rect x="135" y="186" width="86" height="10" rx="5" fill="#E9E0FA" />
                <circle cx="204" cy="91" r="38" fill="#FFD4C7" />
                <path d="M169 88c8-34 63-47 82-12 5 10 5 21 1 33-24 1-54-3-83-21z" fill="#4B315E" />
                <path d="M177 136c18 23 57 24 76 0 14 14 22 34 22 56H155c0-22 8-42 22-56z" fill="#AE99F1" />
                <path d="M151 190h132l18 72H133l18-72z" fill="#F9F7FF" stroke="#C5AEF1" strokeWidth="6" />
                <path d="M192 226h50" stroke="#C5AEF1" strokeLinecap="round" strokeWidth="8" />
                <circle cx="214" cy="222" r="8" fill="#9D0633" />
                <path d="M120 249h198" stroke="#795CBE" strokeLinecap="round" strokeWidth="10" />
                <path d="M88 279h260" stroke="#4B315E" strokeLinecap="round" strokeWidth="14" />
              </svg>

              {floatingCards.map((card, index) => (
                <div
                  className="login-floating-card absolute rounded-2xl bg-white/86 px-4 py-3 font-medium text-[#4f4564] text-sm shadow-[0_16px_34px_rgba(78,55,126,0.14)]"
                  key={card}
                  style={{
                    animationDelay: `${index * 0.45}s`,
                    left: `${index % 2 === 0 ? 5 + index * 8 : 52 + index * 4}%`,
                    top: `${index % 3 === 0 ? 8 + index * 7 : 50 + (index % 3) * 12}%`,
                  }}
                >
                  {card}
                </div>
              ))}
            </div>

            <div className="relative z-10 mt-2 flex flex-wrap items-center gap-2 rounded-3xl bg-white/70 p-4 shadow-sm">
              {flowSteps.map((step, index) => (
                <div className="flex items-center gap-2" key={step}>
                  <span className="rounded-full bg-[#f0e9ff] px-3 py-2 text-[#6d51b8] text-xs">{step}</span>
                  {index < flowSteps.length - 1 && <ArrowRight className="size-3.5 text-[#ae99f1]" />}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
