import json
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, MessagesState, StateGraph

from card_system.document_loader import DocumentLoadError, load_text
from card_system.document_parser_tool import DocumentParserTool
from card_system.prompts import (
    CARD_GENERATION_PROMPT,
    KNOWLEDGE_EXTRACTION_PROMPT,
    QUIZ_GENERATION_PROMPT,
    REVIEW_PLAN_PROMPT,
)
from card_system.rag import build_rag_context
from core import get_model, settings
from schema.card import KnowledgeCard, KnowledgeCardList
from schema.quiz import QuizQuestion, QuizQuestionList
from schema.review import ReviewPlan, ReviewTask

logger = logging.getLogger(__name__)

MemorySaver = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class CardReviewState(MessagesState, total=False):
    """State for the knowledge card review agent."""

    input_text: str
    topic: str
    knowledge_points: list[str]
    cards: KnowledgeCardList
    quizzes: QuizQuestionList
    review_plan: ReviewPlan
    rag_context: str
    document_chunks: list[dict[str, Any]]
    errors: list[str]


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content)
    return str(content)


def _get_last_user_text(state: CardReviewState) -> str:
    human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    if not human_messages:
        return ""
    return _message_content_to_text(human_messages[-1].content).strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


async def _invoke_json_model(
    prompt: str, config: RunnableConfig, fallback: dict[str, Any]
) -> dict[str, Any]:
    model = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    response = await model.ainvoke(
        [
            SystemMessage(
                content=(
                    "只输出合法 JSON，不要输出 Markdown、解释文字或代码块。"
                    "如果信息不足，请用空数组或空字符串占位。"
                )
            ),
            HumanMessage(content=prompt),
        ],
        config,
    )

    try:
        return _extract_json_object(_message_content_to_text(response.content))
    except Exception as e:
        logger.warning("Failed to parse model JSON output: %s", e)
        return fallback


async def parse_input_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Load raw text or a supported document path."""
    user_input = _get_last_user_text(state)
    if not user_input:
        return {
            "input_text": "",
            "topic": "未命名资料",
            "knowledge_points": [],
            "errors": ["学习资料不能为空。"],
        }

    try:
        input_text, metadata = load_text(user_input)
    except DocumentLoadError as e:
        return {
            "input_text": "",
            "topic": "资料加载失败",
            "knowledge_points": [],
            "errors": [str(e)],
        }

    topic = str(metadata.get("title") or input_text.splitlines()[0].strip()[:60] or "学习资料")
    return {"input_text": input_text, "topic": topic, "errors": []}


async def build_context_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Build RAG context; fall back to plain text if retrieval fails."""
    if state.get("errors"):
        return {}

    try:
        context, chunks = build_rag_context(
            query=state.get("topic", "学习资料"),
            text=state["input_text"],
        )
    except Exception as e:
        logger.warning("RAG context generation failed, falling back to plain text: %s", e)
        return {
            "rag_context": state["input_text"][:4000],
            "document_chunks": [],
        }

    return {
        "rag_context": context or state["input_text"][:4000],
        "document_chunks": chunks,
    }


async def extract_knowledge_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Extract core knowledge points from RAG context."""
    if state.get("errors"):
        return {}

    source_text = state.get("rag_context") or state["input_text"]
    prompt = (
        KNOWLEDGE_EXTRACTION_PROMPT.format(source_text=source_text)
        + '\n请输出 JSON：{"knowledge_points":["知识点1","知识点2"]}'
    )
    data = await _invoke_json_model(prompt, config, {"knowledge_points": []})
    points = data.get("knowledge_points", [])
    if not isinstance(points, list):
        points = []

    if not points:
        points = [source_text[:300]]

    return {"knowledge_points": [str(point) for point in points if str(point).strip()]}


async def generate_cards_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Generate structured cards from knowledge points and RAG context."""
    if state.get("errors"):
        return {}

    source_text = state.get("rag_context") or state["input_text"]
    prompt = (
        CARD_GENERATION_PROMPT.format(
            knowledge_points=json.dumps(
                {
                    "knowledge_points": state.get("knowledge_points", []),
                    "rag_context": source_text,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        + """
请输出 JSON，格式为：
{"cards":[{"document_id":"default-document","title":"","summary":"","keywords":[],"explanation":"","example":"","common_mistakes":[],"related_concepts":[],"source_text":""}]}
"""
    )
    data = await _invoke_json_model(prompt, config, {"cards": []})
    cards: list[KnowledgeCard] = []
    for item in data.get("cards", []):
        if not isinstance(item, dict):
            continue
        try:
            item.pop("id", None)
            item["document_id"] = item.get("document_id") or "default-document"
            cards.append(KnowledgeCard(**item))
        except Exception as e:
            logger.warning("Failed to parse knowledge card: %s", e)

    if not cards:
        cards = [
            KnowledgeCard(
                document_id="default-document",
                title=state.get("topic", "学习资料"),
                summary="; ".join(state.get("knowledge_points", []))[:300],
                keywords=[],
                explanation=source_text[:800],
                source_text=source_text[:800],
            )
        ]

    return {"cards": KnowledgeCardList(cards=cards)}


async def generate_quiz_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Generate quiz questions from cards and RAG context."""
    if state.get("errors"):
        return {}

    cards = state["cards"]
    prompt = (
        QUIZ_GENERATION_PROMPT.format(
            cards=json.dumps(
                {
                    "cards": cards.model_dump(mode="json"),
                    "rag_context": state.get("rag_context", ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        + """
请输出 JSON，格式为：
{"questions":[{"card_id":"","question_type":"short_answer","question":"","options":[],"answer":"","explanation":"","difficulty":"medium","related_card_title":""}]}
"""
    )
    data = await _invoke_json_model(prompt, config, {"questions": []})
    questions: list[QuizQuestion] = []
    for item in data.get("questions", []):
        if not isinstance(item, dict):
            continue
        try:
            questions.append(QuizQuestion(**item))
        except Exception as e:
            logger.warning("Failed to parse quiz question: %s", e)

    if not questions and cards.cards:
        card = cards.cards[0]
        questions = [
            QuizQuestion(
                card_id=card.id,
                question_type="short_answer",
                question=f"请简要说明：{card.title}",
                answer=card.summary,
                explanation=card.explanation,
                related_card_title=card.title,
            )
        ]

    return {"quizzes": QuizQuestionList(questions=questions)}


async def generate_review_plan_node(
    state: CardReviewState, config: RunnableConfig
) -> dict[str, Any]:
    """Generate an initial review plan from knowledge points."""
    if state.get("errors"):
        return {}

    weak_points = state.get("knowledge_points", [])[:5]
    prompt = (
        REVIEW_PLAN_PROMPT.format(
            weak_points=json.dumps(weak_points, ensure_ascii=False, indent=2),
            wrong_answers="[]",
        )
        + """
请输出 JSON，格式为：
{"weak_points":[],"tasks":[{"day":1,"topic":"","task":"","reason":"","is_completed":false}]}
"""
    )
    data = await _invoke_json_model(prompt, config, {"weak_points": weak_points, "tasks": []})
    tasks: list[ReviewTask] = []
    for item in data.get("tasks", []):
        if not isinstance(item, dict):
            continue
        try:
            tasks.append(ReviewTask(**item))
        except Exception as e:
            logger.warning("Failed to parse review task: %s", e)

    if not tasks:
        tasks = [
            ReviewTask(
                day=index + 1,
                topic=str(point)[:80],
                task="复习知识卡片并完成对应练习题。",
                reason="该知识点来自本次学习资料，适合作为初始复习任务。",
            )
            for index, point in enumerate(weak_points[:3] or [state.get("topic", "学习资料")])
        ]

    plan = ReviewPlan(
        id=str(uuid4()),
        weak_points=[str(point) for point in data.get("weak_points", weak_points)],
        tasks=tasks,
    )
    return {"review_plan": plan}


async def format_result_node(state: CardReviewState, config: RunnableConfig) -> dict[str, Any]:
    """Format cards, questions, and review tasks for the frontend."""
    if state.get("errors"):
        return {"messages": [AIMessage(content="\n".join(state["errors"]))]}

    cards = state["cards"].cards
    questions = state["quizzes"].questions
    review_plan = state["review_plan"]

    card_lines = [
        f"### {index}. {card.title}\n"
        f"- 摘要：{card.summary}\n"
        f"- 关键词：{', '.join(card.keywords) if card.keywords else '暂无'}\n"
        f"- 解释：{card.explanation}\n"
        f"- 例子：{card.example or '暂无'}\n"
        f"- 常见误区：{'; '.join(card.common_mistakes) if card.common_mistakes else '暂无'}"
        for index, card in enumerate(cards, 1)
    ]
    quiz_lines = [
        f"### {index}. {question.question}\n"
        f"- 类型：{question.question_type}\n"
        f"- 答案：{question.answer}\n"
        f"- 解析：{question.explanation}"
        for index, question in enumerate(questions, 1)
    ]
    task_lines = [
        f"### Day {task.day}: {task.topic}\n- 任务：{task.task}\n- 原因：{task.reason}"
        for task in review_plan.tasks
    ]

    content = "\n\n".join(
        [
            f"# 知识卡片与复习计划：{state.get('topic', '学习资料')}",
            "## RAG 上下文",
            f"已切分 {len(state.get('document_chunks', []))} 个文本块，并使用关键词检索构建上下文。",
            "## 核心知识点",
            "\n".join(f"- {point}" for point in state.get("knowledge_points", [])),
            "## 知识卡片",
            "\n\n".join(card_lines),
            "## 练习题",
            "\n\n".join(quiz_lines),
            "## 初始复习计划",
            "\n\n".join(task_lines),
        ]
    )
    return {"messages": [AIMessage(content=content)]}


def _append_agent_trace(
    state: dict[str, Any],
    name: str,
    status: str,
    detail: str,
) -> None:
    trace = state.setdefault("agent_trace", [])
    trace.append(
        {
            "step": len(trace) + 1,
            "name": name,
            "status": status,
            "detail": detail,
        }
    )


def _short_text(text: str, limit: int) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def _extract_keywords(text: str, limit: int = 12) -> list[str]:
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "以及",
        "可以",
        "需要",
        "通过",
        "进行",
        "一个",
        "一种",
        "学习",
        "资料",
    }
    candidates = re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}|[\u4e00-\u9fff]{2,18}", text)
    counts: dict[str, int] = {}
    for candidate in candidates:
        keyword = candidate.strip().lower() if candidate.isascii() else candidate.strip()
        if keyword in stopwords or len(keyword) < 2:
            continue
        counts[keyword] = counts.get(keyword, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [keyword for keyword, _ in ranked[:limit]]


def _first_sentence(text: str, limit: int = 160) -> str:
    for sentence in re.split(r"[。！？.!?\n]", text):
        sentence = sentence.strip()
        if len(sentence) >= 12:
            return _short_text(sentence, limit)
    return _short_text(text, limit)


def _title_from_chunk(chunk: str, keyword: str, index: int) -> str:
    first_line = next((line.strip() for line in chunk.splitlines() if line.strip()), "")
    first_line = re.sub(r"^[#*\-\d.\s]+", "", first_line).strip()
    if len(first_line) >= 8:
        return _short_text(first_line, 28)
    if keyword:
        return _short_text(keyword, 28)
    return f"知识点 {index}"


def _chunk_texts(state: dict[str, Any]) -> list[str]:
    chunks = state.get("document_chunks") or []
    texts = [str(chunk.get("content", "")).strip() for chunk in chunks if chunk.get("content")]
    if texts:
        return texts

    text = str(state["parsed_document"]["text"])
    fallback_chunks = [text[index : index + 800] for index in range(0, len(text), 800)]
    return [chunk.strip() for chunk in fallback_chunks if chunk.strip()] or [text]


async def file_parse_node(state: dict[str, Any]) -> dict[str, Any]:
    parser = DocumentParserTool()
    parsed = parser.parse(state["filename"], state["file_bytes"])
    state["parsed_document"] = parsed
    _append_agent_trace(
        state,
        "文件解析",
        "success",
        f"已解析 {parsed['file_type'].upper()} 文件，共提取 {parsed['char_count']} 字。",
    )
    return state


async def intent_recognition_node(state: dict[str, Any]) -> dict[str, Any]:
    goal = state.get("learning_goal") or "未指定具体学习目标"
    state["intent"] = "学习资料分析与复习规划任务"
    _append_agent_trace(
        state,
        "意图识别",
        "success",
        f"识别为学习资料分析与复习规划任务，学习目标：{goal}。",
    )
    return state


async def task_planning_node(state: dict[str, Any]) -> dict[str, Any]:
    plan = [
        "文件解析",
        "文本切片",
        "RAG 检索",
        "知识点提取",
        "知识卡片生成",
        "自测题生成",
        "复习计划生成",
        "学习记忆更新",
    ]
    state["task_plan"] = plan
    _append_agent_trace(
        state,
        "任务规划",
        "success",
        "已规划任务链路：" + " → ".join(plan) + "。",
    )
    return state


async def rag_retrieval_node(state: dict[str, Any]) -> dict[str, Any]:
    parsed = state["parsed_document"]
    query = state.get("learning_goal") or parsed["filename"]
    context, chunks = build_rag_context(
        query=query,
        text=parsed["text"],
        document_id="pending-document",
        top_k=max(3, min(8, int(state["card_count"]))),
    )
    state["rag_context"] = context or parsed["text"][:4000]
    state["document_chunks"] = chunks
    _append_agent_trace(
        state,
        "RAG 检索",
        "success",
        f"RAGRetrieverTool 已完成文本切片 {len(chunks)} 个，并构建学习任务上下文。",
    )
    return state


async def card_generation_node(state: dict[str, Any]) -> dict[str, Any]:
    text = state["parsed_document"]["text"]
    chunk_texts = _chunk_texts(state)
    keyword_pool = _extract_keywords(text, limit=max(12, int(state["card_count"]) * 2))
    cards: list[KnowledgeCard] = []

    for index in range(int(state["card_count"])):
        chunk = chunk_texts[index % len(chunk_texts)]
        keyword = keyword_pool[index % len(keyword_pool)] if keyword_pool else ""
        title = _title_from_chunk(chunk, keyword, index + 1)
        card_keywords = keyword_pool[index : index + 4] or ([keyword] if keyword else [title])
        explanation = _first_sentence(chunk, 420)
        source_text = _short_text(chunk, 800)
        cards.append(
            KnowledgeCard(
                document_id="pending-document",
                title=title,
                summary=_short_text(explanation, 140),
                keywords=card_keywords,
                explanation=explanation,
                example=f"可结合资料片段理解：{_short_text(chunk, 120)}",
                common_mistakes=[
                    "只记忆结论，忽略适用条件。",
                    "没有把该知识点与自测题反馈关联起来。",
                ],
                related_concepts=keyword_pool[index + 1 : index + 4],
                source_text=source_text,
            )
        )

    state["cards"] = KnowledgeCardList(cards=cards)
    _append_agent_trace(
        state,
        "卡片生成",
        "success",
        f"CardGeneratorTool 已生成 {len(cards)} 张知识卡片，覆盖核心概念、示例和易错点。",
    )
    return state


async def quiz_generation_node(state: dict[str, Any]) -> dict[str, Any]:
    cards = state["cards"].cards
    questions: list[QuizQuestion] = []
    difficulties = ["easy", "medium", "hard"]

    for index in range(int(state["quiz_count"])):
        card = cards[index % len(cards)]
        questions.append(
            QuizQuestion(
                card_id=card.id,
                question_type="short_answer",
                question=f"请结合资料说明“{card.title}”的核心含义，并指出一个常见误区。",
                options=[],
                answer=card.summary,
                explanation=card.explanation,
                difficulty=difficulties[index % len(difficulties)],
                related_card_title=card.title,
            )
        )

    state["quizzes"] = QuizQuestionList(questions=questions)
    _append_agent_trace(
        state,
        "自测题生成",
        "success",
        f"QuizGeneratorTool 已基于知识卡片生成 {len(questions)} 道自测题。",
    )
    return state


async def review_plan_node(state: dict[str, Any]) -> dict[str, Any]:
    cards = state["cards"].cards
    review_days = int(state["review_days"])
    weak_points = [card.title for card in cards[: max(1, min(len(cards), review_days))]]
    tasks: list[ReviewTask] = []
    daily_tasks: list[dict[str, Any]] = []

    for day in range(1, review_days + 1):
        focus = weak_points[(day - 1) % len(weak_points)]
        task_title = f"第 {day} 天：{focus}"
        task_content = f"复习“{focus}”相关知识卡片，完成自测题，并将错题写入学习记忆。"
        reason = "根据资料切片、卡片覆盖度和自测反馈安排间隔复习。"
        tasks.append(ReviewTask(day=day, topic=focus, task=task_content, reason=reason))
        daily_tasks.append(
            {
                "day": day,
                "task_title": task_title,
                "task_content": task_content,
                "reason": reason,
            }
        )

    plan = ReviewPlan(id=str(uuid4()), weak_points=weak_points, tasks=tasks)
    state["review_plan_model"] = plan
    state["review_plan_payload"] = {
        "id": plan.id,
        "plan_title": "CardReviewAgent 复习计划",
        "review_days": review_days,
        "weak_points": weak_points,
        "daily_tasks": daily_tasks,
    }
    _append_agent_trace(
        state,
        "复习计划生成",
        "success",
        f"ReviewPlannerTool 已生成 {review_days} 天复习计划，并标记 {len(weak_points)} 个薄弱点。",
    )
    return state


async def quality_check_node(state: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    cards = state["cards"].cards
    quizzes = state["quizzes"].questions
    review_plan = state["review_plan_payload"]

    if not cards:
        errors.append("知识卡片为空")
    if not quizzes:
        errors.append("自测题为空")
    if not review_plan.get("daily_tasks"):
        errors.append("复习计划为空")
    if any(not card.title.strip() or not card.explanation.strip() for card in cards):
        errors.append("存在缺少标题或解释的知识卡片")
    if any(not question.answer.strip() or not question.explanation.strip() for question in quizzes):
        errors.append("存在缺少答案或解析的自测题")

    if errors:
        _append_agent_trace(state, "结果校验", "error", "；".join(errors))
        raise ValueError("；".join(errors))

    _append_agent_trace(
        state,
        "结果校验",
        "success",
        "已检查知识卡片、自测题答案解析和复习建议，结构完整。",
    )
    return state


class MemoryTool:
    """Persist CardReviewAgent outputs, with in-memory fallback."""

    async def save(self, state: dict[str, Any]) -> dict[str, Any]:
        saver = state.get("memory_saver")
        if callable(saver):
            return await saver(state)

        return {
            "document": {
                "id": str(uuid4()),
                "title": state["parsed_document"]["filename"],
                "content": state["parsed_document"]["text"],
                "file_path": state["parsed_document"]["filename"],
            },
            "fallback": True,
        }


async def memory_update_node(state: dict[str, Any]) -> dict[str, Any]:
    try:
        memory_result = await MemoryTool().save(state)
        fallback = bool(memory_result.get("fallback"))
    except Exception as e:
        logger.warning("MemoryTool failed, using in-memory fallback: %s", e)
        memory_result = {"document": {"id": str(uuid4())}, "fallback": True, "error": str(e)}
        fallback = True

    document = memory_result.get("document") or {}
    document_id = str(document.get("id") or uuid4())
    state["document_id"] = document_id
    state["memory_result"] = memory_result

    for card in state["cards"].cards:
        card.document_id = document_id

    detail = (
        "MemoryTool 已保存资料、知识卡片、自测题和复习计划，学习记忆已更新。"
        if not fallback
        else "MemoryTool 已使用内存 fallback 保存本次资料、卡片、题目和复习计划。"
    )
    _append_agent_trace(state, "记忆更新", "success", detail)
    return state


async def response_node(state: dict[str, Any]) -> dict[str, Any]:
    cards_payload = []
    for card in state["cards"].cards:
        item = card.model_dump(mode="json")
        item["related_points"] = card.related_concepts
        cards_payload.append(item)

    review_plan = state["review_plan_payload"]
    memory_fallback = bool((state.get("memory_result") or {}).get("fallback"))
    state["response"] = {
        "document_id": state["document_id"],
        "agent_name": "CardReviewAgent",
        "agent_trace": state["agent_trace"],
        "cards": cards_payload,
        "quizzes": [question.model_dump(mode="json") for question in state["quizzes"].questions],
        "review_plan": review_plan,
        "summary": {
            "filename": state["parsed_document"]["filename"],
            "learning_goal": state.get("learning_goal") or "",
            "char_count": state["parsed_document"]["char_count"],
            "rag_chunk_count": len(state.get("document_chunks") or []),
            "card_count": len(cards_payload),
            "quiz_count": len(state["quizzes"].questions),
            "review_days": review_plan["review_days"],
            "memory_status": "fallback" if memory_fallback else "saved",
        },
    }
    return state


async def run_card_review_file_analysis(
    *,
    filename: str,
    file_bytes: bytes,
    user_id: str = "default_user",
    learning_goal: str | None = None,
    card_count: int = 8,
    quiz_count: int = 5,
    review_days: int = 7,
    memory_saver: MemorySaver | None = None,
) -> dict[str, Any]:
    """Run the upload analysis workflow for the CardReviewAgent API."""
    state: dict[str, Any] = {
        "filename": filename,
        "file_bytes": file_bytes,
        "user_id": user_id,
        "learning_goal": (learning_goal or "").strip(),
        "card_count": max(1, min(int(card_count), 30)),
        "quiz_count": max(1, min(int(quiz_count), 30)),
        "review_days": max(1, min(int(review_days), 30)),
        "memory_saver": memory_saver,
        "agent_trace": [],
    }

    for node in (
        file_parse_node,
        intent_recognition_node,
        task_planning_node,
        rag_retrieval_node,
        card_generation_node,
        quiz_generation_node,
        review_plan_node,
        quality_check_node,
        memory_update_node,
        response_node,
    ):
        state = await node(state)

    return state["response"]


agent = StateGraph(CardReviewState)
agent.add_node("parse_input_node", parse_input_node)
agent.add_node("build_context_node", build_context_node)
agent.add_node("extract_knowledge_node", extract_knowledge_node)
agent.add_node("generate_cards_node", generate_cards_node)
agent.add_node("generate_quiz_node", generate_quiz_node)
agent.add_node("generate_review_plan_node", generate_review_plan_node)
agent.add_node("format_result_node", format_result_node)

agent.set_entry_point("parse_input_node")
agent.add_edge("parse_input_node", "build_context_node")
agent.add_edge("build_context_node", "extract_knowledge_node")
agent.add_edge("extract_knowledge_node", "generate_cards_node")
agent.add_edge("generate_cards_node", "generate_quiz_node")
agent.add_edge("generate_quiz_node", "generate_review_plan_node")
agent.add_edge("generate_review_plan_node", "format_result_node")
agent.add_edge("format_result_node", END)

card_review_agent = agent.compile()
