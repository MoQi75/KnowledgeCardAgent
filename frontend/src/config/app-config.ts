import packageJson from "../../package.json";

const currentYear = new Date().getFullYear();

const projectName = "基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统";

export const APP_CONFIG = {
  name: projectName,
  shortName: "知识卡片复习系统",
  version: packageJson.version,
  copyright: `© ${currentYear}, ${projectName}.`,
  meta: {
    title: projectName,
    description: "学习资料解析、知识卡片生成、自测练习、错题分析与复习计划一体化系统。",
  },
};
