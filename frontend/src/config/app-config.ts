import packageJson from "../../package.json";

const currentYear = new Date().getFullYear();

const projectName = "智能知识卡片学习工作台";

export const APP_CONFIG = {
  name: projectName,
  shortName: "AI Knowledge Studio",
  version: packageJson.version,
  copyright: `© ${currentYear}, ${projectName}.`,
  meta: {
    title: projectName,
    description: "基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统。",
  },
};
