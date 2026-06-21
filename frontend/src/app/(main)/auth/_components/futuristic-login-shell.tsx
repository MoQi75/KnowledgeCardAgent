import { ArrowRight, BookOpenCheck } from "lucide-react";

import { LoginForm } from "./login-form";

const formalProjectName = "基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统";
const flowSteps = ["资料输入", "知识提取", "卡片生成", "自测反馈", "复习规划"];
const floatingCards = [
  { label: "RAG 检索", className: "top-[18%] left-[8%]" },
  { label: "知识卡片", className: "top-[20%] right-[10%]" },
  { label: "自测练习", className: "right-[12%] bottom-[30%]" },
  { label: "复习计划", className: "bottom-[22%] left-[12%]" },
];

export function FuturisticLoginShell() {
  return (
    <main className="relative min-h-dvh overflow-hidden bg-[#f7f2ff] text-[#151426]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_12%,rgba(255,255,255,0.72),transparent_26%),radial-gradient(circle_at_82%_14%,rgba(197,174,241,0.34),transparent_28%),radial-gradient(circle_at_74%_86%,rgba(249,238,243,0.8),transparent_30%),linear-gradient(135deg,#f7f2ff_0%,#eee5ff_48%,#f9eef3_100%)]" />
      <div className="login-soft-orb pointer-events-none absolute top-24 -left-24 h-64 w-64 rounded-full bg-[#c5aef1]/24 blur-2xl" />
      <div className="login-soft-orb-delayed pointer-events-none absolute right-8 bottom-8 h-72 w-72 rounded-full bg-[#f4b4c9]/24 blur-2xl" />

      <section className="relative z-10 grid min-h-dvh items-center gap-8 px-5 py-6 sm:px-8 lg:grid-cols-[0.42fr_0.58fr] lg:px-10 xl:px-20">
        <div className="login-panel-enter flex justify-center lg:justify-end">
          <div className="w-full max-w-[490px]">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex size-11 items-center justify-center rounded-2xl bg-[#b70f46] text-white shadow-[0_12px_24px_rgba(183,15,70,0.2)]">
                <BookOpenCheck className="size-5" />
              </div>
              <div>
                <div className="font-semibold text-[#151426] text-lg">知识卡片复习系统</div>
                <div className="text-[#6c627c] text-xs">LangGraph · FastAPI · RAG</div>
              </div>
            </div>

            <div className="rounded-[28px] bg-white/88 p-8 shadow-[0_22px_60px_rgba(88,64,132,0.14)] backdrop-blur-xl xl:p-10">
              <div className="mb-7">
                <h1 className="font-semibold text-3xl text-[#151426] tracking-normal">欢迎登录</h1>
                <p className="mt-3 text-[#6f6680] text-sm">进入知识卡片生成与复习规划系统</p>
              </div>

              <LoginForm />

              <p className="mt-7 text-center text-[#857a98] text-xs">Powered by LangGraph · FastAPI · RAG</p>
            </div>
          </div>
        </div>

        <div className="login-illustration-enter hidden justify-start lg:flex">
          <div className="relative h-[690px] max-h-[calc(100dvh-48px)] w-full max-w-[860px] overflow-hidden rounded-[42px] bg-white/28 p-8 shadow-[0_24px_70px_rgba(109,81,184,0.15)] backdrop-blur-md xl:p-12">
            <div className="absolute -top-16 -right-12 h-48 w-48 rounded-full bg-[#c5aef1]/52" />
            <div className="absolute top-20 right-28 h-20 w-52 rounded-full bg-[#fff6f8]/86" />
            <div className="absolute -bottom-14 left-10 h-48 w-48 rounded-full bg-[#ae99f1]/24" />

            <div className="relative z-10 max-w-[720px]">
              <h2
                aria-label={formalProjectName}
                className="max-w-[680px] font-semibold text-[#151426] text-[48px] leading-[1.12] tracking-normal xl:text-[54px]"
              >
                知识卡片生成与复习规划
                <span className="block">智能体系统</span>
              </h2>
              <p className="mt-5 max-w-[620px] text-[#5d5472] leading-7">
                基于 LangGraph + FastAPI + RAG 构建，支持资料解析、卡片生成、自测反馈与复习规划。
              </p>
            </div>

            <div className="relative z-10 mx-auto mt-6 h-[405px] max-w-[650px]">
              <div className="absolute top-14 left-24 h-44 w-44 rounded-full bg-[#c5aef1]/55" />
              <div className="absolute top-6 left-52 h-20 w-40 rounded-full bg-[#f7d5df]/78" />
              <div className="absolute right-24 bottom-20 h-28 w-64 rounded-full bg-[#d8cff6]/74" />

              <svg
                aria-label="学生在知识卡片空间中学习的插画"
                className="login-illustration-float absolute top-10 left-1/2 h-[335px] w-[390px] -translate-x-1/2"
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
                  className={`login-floating-card absolute rounded-2xl bg-white/88 px-4 py-3 font-medium text-[#4f4564] text-sm shadow-[0_14px_28px_rgba(78,55,126,0.13)] ${card.className}`}
                  key={card.label}
                  style={{ animationDelay: `${index * 0.35}s` }}
                >
                  {card.label}
                </div>
              ))}
            </div>

            <div className="relative z-10 mx-auto flex max-w-[720px] flex-wrap items-center justify-center gap-2 rounded-3xl bg-white/70 p-4 shadow-sm">
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
