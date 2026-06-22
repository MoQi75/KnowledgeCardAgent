import { ArrowRight, BookOpenCheck } from "lucide-react";

import { LoginForm } from "./login-form";

const formalProjectName = "知识卡片生成与复习规划智能体系统";
const flowSteps = ["资料输入", "知识提取", "卡片生成", "自测反馈", "复习规划"];
const floatingCards = [
  { label: "RAG 检索", className: "top-[18%] left-[8%]" },
  { label: "知识卡片", className: "top-[34%] left-[27%]" },
  { label: "自测练习", className: "top-[33%] right-[24%]" },
  { label: "复习计划", className: "right-[10%] bottom-[30%]" },
  { label: "错题分析", className: "bottom-[35%] left-[15%]" },
  { label: "薄弱点", className: "top-[18%] right-[9%]" },
];

export function FuturisticLoginShell() {
  return (
    <main className="relative min-h-dvh overflow-hidden bg-[#f7f2ff] text-[#151426]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_12%,rgba(255,255,255,0.72),transparent_26%),radial-gradient(circle_at_82%_14%,rgba(197,174,241,0.34),transparent_28%),radial-gradient(circle_at_74%_86%,rgba(249,238,243,0.8),transparent_30%),linear-gradient(135deg,#f7f2ff_0%,#eee5ff_48%,#f9eef3_100%)]" />
      <div className="login-soft-orb pointer-events-none absolute top-24 -left-24 h-64 w-64 rounded-full bg-[#c5aef1]/24 blur-2xl" />
      <div className="login-soft-orb-delayed pointer-events-none absolute right-8 bottom-8 h-72 w-72 rounded-full bg-[#f4b4c9]/24 blur-2xl" />

      <section className="relative z-10 grid min-h-dvh items-center gap-2 px-5 py-6 sm:px-8 lg:grid-cols-[0.66fr_0.35fr] lg:px-8 xl:px-12">
        <div className="login-illustration-enter hidden justify-end lg:flex">
          <div className="relative h-[700px] max-h-[calc(100dvh-32px)] w-full max-w-[1040px] overflow-hidden rounded-[42px] bg-white/30 p-8 shadow-[0_24px_70px_rgba(109,81,184,0.15)] backdrop-blur-md xl:p-10">
            <div className="absolute -top-16 -right-12 h-48 w-48 rounded-full bg-[#c5aef1]/50" />
            <div className="absolute top-20 right-28 h-20 w-52 rounded-full bg-[#fff6f8]/86" />
            <div className="absolute -bottom-10 left-10 h-56 w-56 rounded-full bg-[#ae99f1]/22" />
            <div className="absolute top-32 left-8 h-28 w-28 rounded-[36px] bg-white/36" />
            <div className="absolute right-8 bottom-32 h-32 w-32 rounded-full bg-[#f7d5df]/34" />
            <div className="absolute top-[48%] right-[18%] h-14 w-40 rounded-full bg-[#c5aef1]/28" />
            <div className="absolute bottom-24 left-[36%] h-16 w-16 rotate-12 rounded-3xl bg-white/30" />

            <div className="relative z-10 max-w-[820px]">
              <h2
                aria-label={formalProjectName}
                className="hero-title-wrap max-w-[720px] font-extrabold text-[clamp(52px,4.2vw,64px)] leading-[1.1] tracking-[-1.4px]"
              >
                <span className="hero-title-line block text-[#19162b]">知识卡片生成与复习规划</span>
                <span className="hero-title-highlight block bg-[linear-gradient(135deg,#8b5cf6_0%,#d6336c_100%)] bg-clip-text text-transparent">
                  智能体系统
                </span>
              </h2>
              <div className="mt-5 h-1.5 w-28 rounded-full bg-[linear-gradient(135deg,#8b5cf6_0%,#d6336c_100%)]" />
              <p className="mt-5 max-w-none whitespace-nowrap text-[#5d5472] text-sm leading-7 xl:text-base">
                基于 LangGraph + FastAPI + RAG 构建，支持资料解析、卡片生成、自测反馈与复习规划。
              </p>
            </div>

            <div className="relative z-10 mx-auto mt-4 h-[340px] max-w-[720px]">
              <div className="absolute top-14 left-24 h-48 w-48 rounded-full bg-[#c5aef1]/55" />
              <div className="absolute top-6 left-56 h-22 w-44 rounded-full bg-[#f7d5df]/78" />
              <div className="absolute right-20 bottom-20 h-28 w-64 rounded-full bg-[#d8cff6]/76" />

              <svg
                aria-label="学生在知识卡片空间中学习的插画"
                className="login-illustration-float absolute top-0 left-1/2 h-[330px] w-[385px] -translate-x-1/2"
                role="img"
                viewBox="0 0 420 360"
              >
                <title>学生在知识卡片空间中学习</title>
                <path d="M52 284c34-50 96-72 164-64 63 7 112 39 151 84H52z" fill="#D8CFF6" />
                <rect x="105" y="210" width="205" height="38" rx="19" fill="#B70F46" opacity=".9" />
                <rect x="118" y="125" width="156" height="112" rx="24" fill="#fff" />
                <rect x="135" y="144" width="96" height="12" rx="6" fill="#C5AEF1" />
                <rect x="135" y="166" width="116" height="10" rx="5" fill="#E9E0FA" />
                <rect x="135" y="186" width="86" height="10" rx="5" fill="#E9E0FA" />
                <circle cx="204" cy="91" r="38" fill="#FFD4C7" />
                <path d="M169 88c8-34 63-47 82-12 5 10 5 21 1 33-24 1-54-3-83-21z" fill="#4B315E" />
                <path d="M177 136c18 23 57 24 76 0 14 14 22 34 22 56H155c0-22 8-42 22-56z" fill="#AE99F1" />
                <path d="M151 190h132l18 72H133l18-72z" fill="#F9F7FF" stroke="#C5AEF1" strokeWidth="6" />
                <path d="M192 226h50" stroke="#C5AEF1" strokeLinecap="round" strokeWidth="8" />
                <circle cx="214" cy="222" r="8" fill="#B70F46" />
                <path d="M120 249h198" stroke="#795CBE" strokeLinecap="round" strokeWidth="10" />
                <path d="M88 279h260" stroke="#4B315E" strokeLinecap="round" strokeWidth="14" />
              </svg>

              {floatingCards.map((card, index) => (
                <div
                  key={card.label}
                  className={`login-floating-card absolute rounded-2xl bg-white/88 px-4 py-3 font-medium text-[#4f4564] text-sm shadow-[0_14px_28px_rgba(78,55,126,0.13)] ${card.className}`}
                  style={{ animationDelay: `${index * 0.3}s` }}
                >
                  {card.label}
                </div>
              ))}
            </div>

            <div className="absolute right-10 bottom-8 left-10 z-20 mx-auto flex max-w-[760px] flex-wrap items-center justify-center gap-2 rounded-3xl bg-white/82 p-4 shadow-[0_14px_36px_rgba(98,72,145,0.12)]">
              {flowSteps.map((step, index) => (
                <div className="flex items-center gap-2" key={step}>
                  <span className="rounded-full bg-[#f0e9ff] px-3 py-2 text-[#6d51b8] text-xs">{step}</span>
                  {index < flowSteps.length - 1 && <ArrowRight className="size-3.5 text-[#ae99f1]" />}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="login-panel-enter flex justify-center lg:justify-end">
          <div className="w-full max-w-[490px] text-center">
            <div className="mb-6 flex items-center justify-center gap-3">
              <div className="flex size-11 items-center justify-center rounded-2xl bg-[#b70f46] text-white shadow-[0_12px_24px_rgba(183,15,70,0.2)]">
                <BookOpenCheck className="size-5" />
              </div>
              <div className="text-left">
                <div className="font-semibold text-[#151426] text-lg">知识卡片复习系统</div>
                <div className="text-[#6c627c] text-xs">LangGraph + FastAPI + RAG</div>
              </div>
            </div>

            <div className="rounded-[28px] bg-white/88 p-8 text-left shadow-[0_22px_60px_rgba(88,64,132,0.14)] backdrop-blur-xl xl:p-10">
              <div className="mb-7 text-center">
                <h1 className="font-semibold text-3xl text-[#151426] tracking-normal">欢迎登录</h1>
                <p className="mt-3 text-[#6f6680] text-sm">进入知识卡片生成与复习规划系统</p>
              </div>

              <LoginForm />

              <p className="mt-7 text-center text-[#857a98] text-xs">Powered by LangGraph + FastAPI + RAG</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
