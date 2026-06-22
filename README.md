# 基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统

中文 | [English](#cardreviewagent-knowledge-card-generation-and-review-planning-system)

本项目是一个面向学习资料处理的智能体系统。用户可以上传 PDF、DOCX、TXT 或 Markdown 学习资料，由 `CardReviewAgent` 自动完成资料解析、RAG 检索、知识卡片生成、自测题生成、复习计划生成和学习记忆更新。

## 核心能力

- `CardReviewAgent` 智能体工作流：文件解析、意图识别、任务规划、RAG 检索、卡片生成、自测题生成、复习计划生成、结果校验、记忆更新。
- 多格式学习资料上传：支持 `.pdf`、`.docx`、`.txt`、`.md`、`.markdown`。
- 知识卡片生成：输出标题、摘要、关键词、解释、示例、常见误区、相关知识点和原文片段。
- 自测题生成：基于知识卡片生成问答题，包含答案、解析、难度和关联卡片。
- 复习计划生成：根据卡片和薄弱点生成多天复习任务。
- 智能体执行过程展示：前端展示 `agent_trace`，体现每一步工具调用和状态。
- 学习记忆：优先保存到 PostgreSQL，数据库不可用时提供内存 fallback。

## 技术栈

- 后端：FastAPI、LangGraph、Pydantic、PostgreSQL、pypdf、python-docx
- 前端：Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、lucide-react
- RAG：当前提供关键词检索 fallback，保留后续接入向量库的结构
- 包管理：uv、npm

## 关键目录

```text
src/
  agents/card_review_agent.py          # CardReviewAgent 智能体流程
  card_system/document_parser_tool.py  # PDF/DOCX/TXT/Markdown 解析工具
  card_system/rag.py                   # 文本切片和 RAG 检索 fallback
  card_system/storage.py               # 知识卡片系统持久化
  service/service.py                   # FastAPI 服务和接口
  schema/                              # 后端请求/响应模型

frontend/
  src/app/(main)/dashboard/default/    # 智能体学习仪表盘
  src/app/(main)/dashboard/_components/knowledge-studio/
                                      # 资料库、知识卡片、自测、复习计划页面
  src/lib/card-system-api.ts           # 前端 API 封装
```

## 快速启动

### 1. 安装后端依赖

```sh
uv sync
```

如需连接数据库，请在 `.env` 中配置 PostgreSQL：

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
```

### 2. 启动后端

```sh
python src/run_service.py
```

默认服务地址：`http://localhost:8080`

### 3. 安装并启动前端

```sh
cd frontend
npm install
npm run dev
```

默认前端地址：`http://localhost:3000/dashboard`

如果后端不是默认地址，请设置：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

## 上传资料智能分析接口

```http
POST /card-system/agent/analyze-file
Content-Type: multipart/form-data
```

请求参数：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `file` | 上传文件，支持 PDF/DOCX/TXT/Markdown | 必填 |
| `user_id` | 用户 ID | `default_user` |
| `learning_goal` | 学习目标 | 可选 |
| `card_count` | 知识卡片数量 | `8` |
| `quiz_count` | 自测题数量 | `5` |
| `review_days` | 复习计划天数 | `7` |

响应字段：

```json
{
  "document_id": "...",
  "agent_name": "CardReviewAgent",
  "agent_trace": [],
  "cards": [],
  "quizzes": [],
  "review_plan": {},
  "summary": {}
}
```

`agent_trace` 用于前端展示智能体执行过程，每一步包含：

```json
{
  "step": 1,
  "name": "文件解析",
  "status": "success",
  "detail": "已解析 PDF 文件，共提取 3264 字。"
}
```

## 前端页面

- `/dashboard/default`：CardReviewAgent 智能体学习仪表盘
- `/dashboard/documents`：资料库与资料智能分析
- `/dashboard/cards`：知识卡片
- `/dashboard/quiz`：自测题
- `/dashboard/wrong-questions`：错题本
- `/dashboard/review-plan`：复习计划
- `/dashboard/stats`：学习统计
- `/dashboard/settings`：系统设置

## 检查命令

后端：

```sh
python -m compileall src
```

前端：

```sh
cd frontend
npm run lint
npm run build
```

---

# CardReviewAgent Knowledge Card Generation and Review Planning System

[中文](#基于-langgraph--fastapi--rag-的知识卡片生成与复习规划智能体系统) | English

This project is an agentic learning system for study material analysis. Users can upload PDF, DOCX, TXT, or Markdown files, and `CardReviewAgent` automatically parses the material, retrieves RAG context, generates knowledge cards, creates quiz questions, builds a review plan, and updates learning memory.

## Core Capabilities

- `CardReviewAgent` workflow: file parsing, intent recognition, task planning, RAG retrieval, card generation, quiz generation, review planning, quality check, and memory update.
- Multi-format uploads: `.pdf`, `.docx`, `.txt`, `.md`, and `.markdown`.
- Knowledge card generation: title, summary, keywords, explanation, example, common mistakes, related points, and source text.
- Quiz generation: question, answer, explanation, difficulty, and related card title.
- Review planning: daily review tasks based on generated cards and weak points.
- Agent trace visualization: the frontend displays `agent_trace` to show each agent step and tool call.
- Learning memory: PostgreSQL persistence is used first, with an in-memory fallback when storage is unavailable.

## Tech Stack

- Backend: FastAPI, LangGraph, Pydantic, PostgreSQL, pypdf, python-docx
- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, lucide-react
- RAG: keyword retrieval fallback with a structure ready for vector database integration
- Package management: uv, npm

## Key Directories

```text
src/
  agents/card_review_agent.py          # CardReviewAgent workflow
  card_system/document_parser_tool.py  # PDF/DOCX/TXT/Markdown parser
  card_system/rag.py                   # Text chunking and RAG fallback
  card_system/storage.py               # Knowledge card persistence
  service/service.py                   # FastAPI service and routes
  schema/                              # Backend request/response schemas

frontend/
  src/app/(main)/dashboard/default/    # Agent learning dashboard
  src/app/(main)/dashboard/_components/knowledge-studio/
                                      # Documents, cards, quiz, review pages
  src/lib/card-system-api.ts           # Frontend API client
```

## Quick Start

### 1. Install backend dependencies

```sh
uv sync
```

Configure PostgreSQL in `.env` if persistence is required:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
```

### 2. Start the backend

```sh
python src/run_service.py
```

Default service URL: `http://localhost:8080`

### 3. Install and start the frontend

```sh
cd frontend
npm install
npm run dev
```

Default frontend URL: `http://localhost:3000/dashboard`

Set the backend URL when needed:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

## File Analysis API

```http
POST /card-system/agent/analyze-file
Content-Type: multipart/form-data
```

Request fields:

| Field | Description | Default |
| --- | --- | --- |
| `file` | Uploaded PDF/DOCX/TXT/Markdown file | Required |
| `user_id` | User ID | `default_user` |
| `learning_goal` | Learning goal | Optional |
| `card_count` | Number of knowledge cards | `8` |
| `quiz_count` | Number of quiz questions | `5` |
| `review_days` | Number of review days | `7` |

Response shape:

```json
{
  "document_id": "...",
  "agent_name": "CardReviewAgent",
  "agent_trace": [],
  "cards": [],
  "quizzes": [],
  "review_plan": {},
  "summary": {}
}
```

Each `agent_trace` item follows this structure:

```json
{
  "step": 1,
  "name": "File Parsing",
  "status": "success",
  "detail": "Parsed the PDF file and extracted 3264 characters."
}
```

## Frontend Pages

- `/dashboard/default`: CardReviewAgent learning dashboard
- `/dashboard/documents`: document library and file analysis
- `/dashboard/cards`: knowledge cards
- `/dashboard/quiz`: quiz questions
- `/dashboard/wrong-questions`: wrong question notebook
- `/dashboard/review-plan`: review plan
- `/dashboard/stats`: learning statistics
- `/dashboard/settings`: system settings

## Validation

Backend:

```sh
python -m compileall src
```

Frontend:

```sh
cd frontend
npm run lint
npm run build
```

