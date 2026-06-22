# 基于 LangGraph + FastAPI + RAG 的知识卡片生成与复习规划智能体系统

中文 | [English](#cardreviewagent-knowledge-card-generation-and-review-planning-system)

本项目是一个面向学习资料处理与复习规划场景的智能体系统。系统支持上传 PDF、DOCX、TXT、Markdown 等学习资料，由 `CardReviewAgent` 智能体自动完成资料解析、RAG 检索、知识点提取、知识卡片生成、自测题生成和复习计划制定，帮助用户构建从“资料输入”到“复习反馈”的完整学习闭环。

---

## 项目简介

在日常课程学习、实习培训和资料复习过程中，学生往往需要阅读大量 PDF 课件、Word 文档、实验指导书和课程讲义。传统方式下，学习者需要手动整理重点、归纳知识点、制作复习卡片并安排复习计划，过程重复且效率较低。

针对这一问题，本项目设计并实现了一个基于大模型与智能体技术的知识卡片生成与复习规划系统。系统以 LangGraph 作为智能体流程编排核心，以 FastAPI 作为后端接口服务，以 RAG 检索增强技术作为学习资料理解支撑。用户上传学习资料后，系统会自动解析文件内容，对文本进行切片和检索，提取核心知识点，并进一步生成结构化知识卡片、自测练习题和阶段性复习计划。

与普通的大模型问答系统不同，本项目重点体现智能体的任务规划、工具调用、结果校验和学习记忆能力，使系统能够围绕用户的学习目标完成连续的学习辅助任务。项目的核心价值在于将零散学习资料转化为可复习、可练习、可追踪的结构化学习内容，并为后续学习统计和个性化学习路径优化提供数据基础。

---

## 功能特性

- 支持上传 PDF、DOCX、TXT、Markdown 等学习资料，满足常见课程资料、实验文档和复习讲义的处理需求。
- 支持对上传文件进行自动解析，提取文档正文内容，并对文本进行切片处理，为后续 RAG 检索和知识点分析提供基础。
- 基于 RAG 检索增强技术，从学习资料中提取与用户学习目标相关的上下文内容，减少生成结果脱离资料的问题。
- 基于 `CardReviewAgent` 智能体完成资料分析任务，体现意图识别、任务规划、工具调用、结果校验和记忆更新等智能体能力。
- 自动生成结构化知识卡片，每张卡片包含标题、摘要、关键词、详细解释、示例说明、易错点、关联知识点和原文片段。
- 自动生成自测练习题，包含题目类型、题干、选项、标准答案、解析、难度和关联知识卡片。
- 根据知识卡片、自测结果和薄弱知识点生成个性化复习计划，帮助用户安排阶段性复习任务。
- 支持错题记录与薄弱点分析，为后续复习计划调整和学习统计提供依据。
- 前端提供可视化页面，展示资料上传、智能体执行过程、知识卡片、自测题、复习计划和学习统计等内容。
- 后端提供标准化 API 接口，支持前端调用文件上传、智能分析、卡片生成、自测批改和复习计划生成等功能。
- 支持通过 `agent_trace` 展示智能体执行过程，让用户看到系统从文件解析到工具调用、结果生成和学习记忆更新的完整流程。

---

## 技术栈

### 前端

当前前端采用 Next.js App Router + React + TypeScript 构建，负责提供用户交互界面和学习数据可视化展示。前端页面包括登录页、智能体学习仪表盘、资料库、知识卡片、自测练习、错题本、复习计划、学习统计和系统设置等模块，并通过统一 API 封装调用后端 FastAPI 服务。

前端主要技术包括：

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui 风格组件
- lucide-react 图标
- Recharts
- Biome

### 后端

后端采用 Python + FastAPI 构建接口服务，负责接收前端请求、处理上传文件、调用智能体流程、管理数据存储并返回结构化分析结果。核心智能体 `CardReviewAgent` 基于 LangGraph 思路组织文件解析、意图识别、任务规划、RAG 检索、知识卡片生成、自测题生成、复习计划生成、结果校验和记忆更新等步骤。

后端主要技术包括：

- Python
- FastAPI
- LangGraph
- Pydantic
- RAG 检索增强
- pypdf，用于 PDF 文件解析
- python-docx，用于 DOCX 文件解析
- python-multipart，用于文件上传接口支持
- OpenAI API / DeepSeek API / 兼容 OpenAI 协议模型，可根据 `.env` 实际配置选择

### 数据存储与其他工具

项目包含 LangGraph 运行记忆和知识卡片业务数据两类存储需求。本地开发可使用 SQLite 启动基础服务；部署或完整业务持久化场景可接入 PostgreSQL 或 MySQL，用于保存学习资料、知识卡片、自测题、答题记录、错题记录和复习计划等数据。RAG 检索部分当前提供轻量级关键词检索 fallback，并保留后续接入 ChromaDB 或其他向量检索方案的结构。

其他相关工具包括：

- Git / GitHub
- Docker / Docker Compose
- uv
- npm
- SQLite / PostgreSQL / MySQL
- ChromaDB 或其他向量检索工具
- `.env` 环境变量配置文件

---

## 项目结构

```text
KnowledgeCardAgent/
├── frontend/                              # 前端项目目录
│   ├── package.json                       # 前端依赖与脚本
│   ├── next.config.mjs                    # Next.js 配置
│   ├── biome.json                         # 前端 lint/format 配置
│   └── src/
│       ├── app/                           # Next.js App Router 页面
│       │   └── (main)/
│       │       ├── auth/                  # 登录与注册页面
│       │       └── dashboard/             # 学习工作台页面
│       │           ├── default/           # CardReviewAgent 智能体学习仪表盘
│       │           ├── documents/         # 资料库与资料智能分析
│       │           ├── cards/             # 知识卡片页面
│       │           ├── quiz/              # 自测练习页面
│       │           ├── wrong-questions/   # 错题本页面
│       │           ├── review-plan/       # 复习计划页面
│       │           ├── stats/             # 学习统计页面
│       │           └── settings/          # 系统设置页面
│       ├── components/                    # 前端通用组件
│       ├── lib/
│       │   └── card-system-api.ts         # 知识卡片系统 API 封装
│       ├── navigation/                    # 侧边栏导航配置
│       └── stores/                        # 前端偏好设置状态
│
├── src/                                   # 后端源码目录
│   ├── agents/
│   │   └── card_review_agent.py           # CardReviewAgent 智能体流程
│   ├── card_system/                       # 知识卡片业务模块
│   │   ├── document_parser_tool.py        # PDF/DOCX/TXT/Markdown 解析工具
│   │   ├── document_loader.py             # 文档加载辅助模块
│   │   ├── rag.py                         # 文本切片与 RAG 检索 fallback
│   │   ├── card_generator.py              # 知识卡片生成模块
│   │   ├── quiz_generator.py              # 自测题生成模块
│   │   ├── review_planner.py              # 复习计划生成模块
│   │   ├── answer_checker.py              # 答案批改模块
│   │   ├── storage.py                     # 知识卡片业务持久化模块
│   │   └── db_schema.sql                  # 业务数据表结构
│   ├── schema/                            # Pydantic 请求/响应模型
│   ├── service/
│   │   └── service.py                     # FastAPI 应用与接口路由
│   ├── memory/                            # LangGraph 记忆存储适配
│   ├── run_service.py                     # 后端服务启动入口
│   └── streamlit_app.py                   # 可选 Streamlit 演示入口
│
├── tests/                                 # 后端测试目录
├── docker/                                # Dockerfile 配置
├── docs/                                  # 项目文档
├── data/                                  # 示例数据或本地资料
├── scripts/                               # 辅助脚本
├── compose.yaml                           # Docker Compose 配置
├── pyproject.toml                         # Python 项目与依赖配置
├── uv.lock                                # uv 锁文件
├── .env.example                           # 环境变量示例
├── .gitignore                             # Git 忽略配置
└── README.md                              # 项目说明文档
```

---

## 核心智能体流程

`CardReviewAgent` 的执行过程通过 `agent_trace` 返回给前端展示，主要包含以下节点：

1. 文件解析：解析 PDF、DOCX、TXT 或 Markdown 文件，提取正文内容。
2. 意图识别：识别当前任务为学习资料分析与复习规划任务。
3. 任务规划：规划资料解析、文本切片、RAG 检索、知识提取、卡片生成、自测反馈和复习计划。
4. RAG 检索：对文本进行切片，并构建与学习目标相关的上下文。
5. 卡片生成：根据资料内容生成结构化知识卡片。
6. 自测题生成：根据知识卡片生成自测练习题。
7. 复习计划生成：根据知识点和薄弱项生成阶段性复习任务。
8. 结果校验：检查知识卡片、题目答案、解析和复习建议是否完整。
9. 记忆更新：保存资料、卡片、题目、答题记录、错题和复习计划。

`agent_trace` 示例：

```json
{
  "step": 1,
  "name": "文件解析",
  "status": "success",
  "detail": "已解析 PDF 文件，共提取 3264 字。"
}
```

---

## 后端接口

### 上传资料智能分析

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
| `card_count` | 生成知识卡片数量 | `8` |
| `quiz_count` | 生成自测题数量 | `5` |
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

### 其他知识卡片接口

- `POST /card-system/documents`：创建学习资料记录
- `GET /card-system/documents`：获取资料列表
- `POST /card-system/cards/generate`：生成知识卡片
- `GET /card-system/cards`：获取知识卡片列表
- `POST /card-system/quiz/generate`：生成自测题
- `GET /card-system/quiz`：获取自测题列表
- `POST /card-system/quiz/submit`：提交答案并批改
- `GET /card-system/wrong-questions`：获取错题记录
- `POST /card-system/review-plan/generate`：生成复习计划
- `GET /card-system/study-summary`：获取学习统计摘要

---

## 快速启动

### 1. 一键启动

Windows 本地开发可直接运行根目录脚本，脚本会启动 FastAPI 后端和 Next.js 前端，并等待健康检查通过：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Restart
```

默认地址：

```text
后端：http://127.0.0.1:8080/health
前端：http://127.0.0.1:3001/dashboard/default
```

如果本机 `8080` 已被占用，可指定后端端口：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Restart -BackendPort 8081
```

首次启动并需要安装依赖时，可增加 `-Install`：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Install -Restart
```

### 2. 手动配置环境变量

如需手动启动，先复制 `.env.example` 为 `.env`，并至少配置一种可用模型。仅本地启动后端时，建议先使用 SQLite 作为 LangGraph 运行记忆：

```env
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=checkpoints.db
USE_FAKE_MODEL=true
```

如果使用真实大模型，请在 `.env` 中配置相应 API Key，例如：

```env
OPENAI_API_KEY=your-api-key
```

前端默认请求 `http://localhost:8080`，如需修改后端地址，可在前端环境变量中设置：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

### 3. 安装后端依赖

```sh
uv sync
```

### 4. 启动后端

```sh
uv run python src/run_service.py
```

默认后端地址：

```text
http://localhost:8080
```

健康检查：

```text
http://localhost:8080/health
```

### 5. 安装并启动前端

```sh
cd frontend
npm install
npm run dev
```

默认前端地址：

```text
http://localhost:3000/dashboard/default
```

---

## 检查命令

后端编译检查：

```sh
uv run python -m compileall src
```

前端 lint：

```sh
cd frontend
npm run lint
```

前端生产构建：

```sh
cd frontend
npm run build
```

---

# CardReviewAgent Knowledge Card Generation and Review Planning System

[中文](#基于-langgraph--fastapi--rag-的知识卡片生成与复习规划智能体系统) | English

This project is an agentic learning system for study material analysis and review planning. It supports uploading PDF, DOCX, TXT, and Markdown learning materials. `CardReviewAgent` automatically parses the document, retrieves RAG context, extracts knowledge points, generates knowledge cards, creates quiz questions, and builds a review plan, helping users form a complete learning loop from material input to review feedback.

---

## Overview

Students often need to read large amounts of course slides, Word documents, experiment guides, and lecture notes. In a traditional workflow, learners manually identify key points, summarize concepts, create review cards, and plan review schedules. This process is repetitive and inefficient.

This project solves that problem with a knowledge card generation and review planning system based on LLM agents. LangGraph is used as the workflow orchestration layer, FastAPI provides backend services, and RAG retrieval helps ground the analysis in uploaded learning materials. After a user uploads a document, the system parses the content, chunks and retrieves relevant text, extracts core knowledge points, then generates structured knowledge cards, quiz questions, and a staged review plan.

Unlike a simple chatbot, this project focuses on agent capabilities such as task planning, tool invocation, quality checking, and learning memory. It turns scattered learning materials into structured content that can be reviewed, practiced, tracked, and reused.

---

## Features

- Upload PDF, DOCX, TXT, and Markdown learning materials.
- Parse uploaded files and extract document text for chunking, RAG retrieval, and knowledge analysis.
- Use RAG retrieval to build context related to the user's learning goal.
- Run the `CardReviewAgent` workflow with intent recognition, task planning, tool invocation, quality checking, and memory update.
- Generate structured knowledge cards with title, summary, keywords, explanation, example, common mistakes, related points, and source text.
- Generate quiz questions with question type, options, answer, explanation, difficulty, and related card title.
- Build personalized review plans based on cards, quizzes, and weak points.
- Record wrong questions and weak points for review planning and learning statistics.
- Provide frontend pages for file upload, agent trace visualization, knowledge cards, quizzes, review plans, and learning statistics.
- Expose standardized FastAPI endpoints for document upload, agent analysis, card generation, answer checking, and review planning.
- Return `agent_trace` so the frontend can display the complete workflow from file parsing to tool calls, result generation, and learning memory update.

---

## Tech Stack

### Frontend

The current frontend is built with Next.js App Router, React, and TypeScript. It provides the login page, learning dashboard, document library, knowledge cards, quizzes, wrong question notebook, review plan, learning statistics, and settings pages. It calls the FastAPI backend through a centralized API client.

Main frontend technologies:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui-style components
- lucide-react
- Recharts
- Biome

### Backend

The backend is built with Python and FastAPI. It handles frontend requests, uploaded files, agent workflow execution, persistence, and structured responses. The core `CardReviewAgent` organizes file parsing, intent recognition, task planning, RAG retrieval, card generation, quiz generation, review planning, quality checking, and memory update.

Main backend technologies:

- Python
- FastAPI
- LangGraph
- Pydantic
- RAG retrieval
- pypdf for PDF parsing
- python-docx for DOCX parsing
- python-multipart for file upload support
- OpenAI API / DeepSeek API / OpenAI-compatible models, depending on `.env` configuration

### Storage and Tools

The project has two storage concerns: LangGraph runtime memory and knowledge-card business data. SQLite can be used for local development startup. PostgreSQL or MySQL can be connected for deployment or full business persistence. The RAG module currently includes a lightweight keyword retrieval fallback and keeps the structure ready for ChromaDB or other vector retrieval systems.

Related tools:

- Git / GitHub
- Docker / Docker Compose
- uv
- npm
- SQLite / PostgreSQL / MySQL
- ChromaDB or other vector retrieval tools
- `.env` configuration

---

## Project Structure

```text
KnowledgeCardAgent/
├── frontend/                              # Frontend project
│   ├── package.json                       # Frontend dependencies and scripts
│   ├── next.config.mjs                    # Next.js config
│   ├── biome.json                         # Frontend lint/format config
│   └── src/
│       ├── app/                           # Next.js App Router pages
│       │   └── (main)/
│       │       ├── auth/                  # Login and register pages
│       │       └── dashboard/             # Learning workspace pages
│       │           ├── default/           # CardReviewAgent dashboard
│       │           ├── documents/         # Document library and analysis
│       │           ├── cards/             # Knowledge cards
│       │           ├── quiz/              # Quizzes
│       │           ├── wrong-questions/   # Wrong question notebook
│       │           ├── review-plan/       # Review plan
│       │           ├── stats/             # Learning statistics
│       │           └── settings/          # Settings
│       ├── components/                    # Shared frontend components
│       ├── lib/
│       │   └── card-system-api.ts         # Knowledge card API client
│       ├── navigation/                    # Sidebar navigation config
│       └── stores/                        # Preference state stores
│
├── src/                                   # Backend source
│   ├── agents/
│   │   └── card_review_agent.py           # CardReviewAgent workflow
│   ├── card_system/                       # Knowledge card business modules
│   │   ├── document_parser_tool.py        # PDF/DOCX/TXT/Markdown parser
│   │   ├── document_loader.py             # Document loading helper
│   │   ├── rag.py                         # Text chunking and RAG fallback
│   │   ├── card_generator.py              # Knowledge card generation
│   │   ├── quiz_generator.py              # Quiz generation
│   │   ├── review_planner.py              # Review plan generation
│   │   ├── answer_checker.py              # Answer checking
│   │   ├── storage.py                     # Business persistence
│   │   └── db_schema.sql                  # Business database schema
│   ├── schema/                            # Pydantic request/response schemas
│   ├── service/
│   │   └── service.py                     # FastAPI app and routes
│   ├── memory/                            # LangGraph memory adapters
│   ├── run_service.py                     # Backend service entrypoint
│   └── streamlit_app.py                   # Optional Streamlit demo
│
├── tests/                                 # Backend tests
├── docker/                                # Dockerfiles
├── docs/                                  # Documentation
├── data/                                  # Sample data or local materials
├── scripts/                               # Utility scripts
├── compose.yaml                           # Docker Compose config
├── pyproject.toml                         # Python project config
├── uv.lock                                # uv lockfile
├── .env.example                           # Environment variable example
├── .gitignore                             # Git ignore rules
└── README.md                              # Project README
```

---

## Core Agent Workflow

`CardReviewAgent` returns `agent_trace` for frontend visualization. The workflow includes:

1. File parsing: parse PDF, DOCX, TXT, or Markdown and extract text.
2. Intent recognition: identify the current task as learning material analysis and review planning.
3. Task planning: plan document parsing, text chunking, RAG retrieval, knowledge extraction, card generation, quiz feedback, and review planning.
4. RAG retrieval: chunk the document and build context related to the learning goal.
5. Card generation: generate structured knowledge cards from the material.
6. Quiz generation: generate quiz questions from the cards.
7. Review planning: build staged daily review tasks.
8. Quality check: validate cards, answers, explanations, and review suggestions.
9. Memory update: save documents, cards, questions, answer records, wrong questions, and review plans.

Example `agent_trace` item:

```json
{
  "step": 1,
  "name": "File Parsing",
  "status": "success",
  "detail": "Parsed the PDF file and extracted 3264 characters."
}
```

---

## Backend API

### File Analysis

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

### Other Knowledge Card APIs

- `POST /card-system/documents`: create a learning document
- `GET /card-system/documents`: list learning documents
- `POST /card-system/cards/generate`: generate knowledge cards
- `GET /card-system/cards`: list knowledge cards
- `POST /card-system/quiz/generate`: generate quiz questions
- `GET /card-system/quiz`: list quiz questions
- `POST /card-system/quiz/submit`: submit and check an answer
- `GET /card-system/wrong-questions`: list wrong questions
- `POST /card-system/review-plan/generate`: generate a review plan
- `GET /card-system/study-summary`: get study summary

---

## Quick Start

### 1. One-command startup

On Windows, run the root startup script to start both the FastAPI backend and the Next.js frontend. The script waits for both health checks:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Restart
```

Default URLs:

```text
Backend:  http://127.0.0.1:8080/health
Frontend: http://127.0.0.1:3001/dashboard/default
```

If port `8080` is already occupied, provide another backend port:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Restart -BackendPort 8081
```

Use `-Install` on first startup when dependencies need to be installed:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1 -Install -Restart
```

### 2. Manual environment configuration

For manual startup, copy `.env.example` to `.env` and configure at least one model provider. For local development, SQLite is recommended for LangGraph runtime memory:

```env
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=checkpoints.db
USE_FAKE_MODEL=true
```

For real model calls, configure the corresponding API key:

```env
OPENAI_API_KEY=your-api-key
```

The frontend calls `http://localhost:8080` by default. Override it when needed:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

### 3. Install backend dependencies

```sh
uv sync
```

### 4. Start the backend

```sh
uv run python src/run_service.py
```

Default backend URL:

```text
http://localhost:8080
```

Health check:

```text
http://localhost:8080/health
```

### 5. Install and start the frontend

```sh
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://localhost:3000/dashboard/default
```

---

## Validation

Backend compile check:

```sh
uv run python -m compileall src
```

Frontend lint:

```sh
cd frontend
npm run lint
```

Frontend production build:

```sh
cd frontend
npm run build
```
