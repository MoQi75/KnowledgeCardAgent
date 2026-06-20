import json
import logging
import re
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, MessagesState, StateGraph

from card_system.prompts import (
    CARD_GENERATION_PROMPT,
    KNOWLEDGE_EXTRACTION_PROMPT,
    QUIZ_GENERATION_PROMPT,
    REVIEW_PLAN_PROMPT,
)
from core import get_model, settings
from schema.card import KnowledgeCard, KnowledgeCardList
from schema.quiz import QuizQuestion, QuizQuestionList
from schema.review import ReviewPlan, ReviewTask

logger = logging.getLogger(__name__)


class CardReviewState(MessagesState, total=False):
    """知识卡片复习智能体的运行状态。"""

    input_text: str
    topic: str
    knowledge_points: list[str]
    cards: KnowledgeCardList
    quizzes: QuizQuestionList
    review_plan: ReviewPlan
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
    """从模型输出中提取 JSON 对象，兼容 ```json 代码块。"""
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
                    "你只输出合法 JSON，不要输出 Markdown、解释文字或代码块。"
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


async def parse_input_node(state: CardReviewState, config: RunnableConfig) -> CardReviewState:
    """接收学习资料文本，并检查空输入。"""
    input_text = _get_last_user_text(state)
    if not input_text:
        return {
            "input_text": "",
            "topic": "未命名资料",
            "knowledge_points": [],
            "errors": ["学习资料不能为空。"],
        }

    topic = input_text.splitlines()[0].strip()[:60] or "学习资料"
    return {"input_text": input_text, "topic": topic, "errors": []}


async def extract_knowledge_node(
    state: CardReviewState, config: RunnableConfig
) -> CardReviewState:
    """从学习资料中提取核心知识点。"""
    if state.get("errors"):
        return {}

    prompt = (
        KNOWLEDGE_EXTRACTION_PROMPT.format(source_text=state["input_text"])
        + '\n请输出 JSON：{"knowledge_points":["知识点1","知识点2"]}'
    )
    data = await _invoke_json_model(prompt, config, {"knowledge_points": []})
    points = data.get("knowledge_points", [])
    if not isinstance(points, list):
        points = []

    # 兜底：模型未返回结构化结果时，用输入文本生成一个基础知识点。
    if not points:
        points = [state["input_text"][:300]]

    return {"knowledge_points": [str(point) for point in points if str(point).strip()]}


async def generate_cards_node(state: CardReviewState, config: RunnableConfig) -> CardReviewState:
    """根据知识点生成结构化知识卡片。"""
    if state.get("errors"):
        return {}

    prompt = (
        CARD_GENERATION_PROMPT.format(
            knowledge_points=json.dumps(
                state.get("knowledge_points", []), ensure_ascii=False, indent=2
            )
        )
        + """
请输出 JSON，格式为：
{"cards":[{"document_id":"doc-1","title":"","summary":"","keywords":[],"explanation":"","example":"","common_mistakes":[],"related_concepts":[],"source_text":""}]}
"""
    )
    data = await _invoke_json_model(prompt, config, {"cards": []})
    cards: list[KnowledgeCard] = []
    for item in data.get("cards", []):
        if not isinstance(item, dict):
            continue
        try:
            cards.append(KnowledgeCard(document_id="default-document", **item))
        except Exception as e:
            logger.warning("Failed to parse knowledge card: %s", e)

    if not cards:
        cards = [
            KnowledgeCard(
                document_id="default-document",
                title=state.get("topic", "学习资料"),
                summary="; ".join(state.get("knowledge_points", []))[:300],
                keywords=[],
                explanation=state.get("input_text", "")[:800],
                source_text=state.get("input_text", "")[:800],
            )
        ]

    return {"cards": KnowledgeCardList(cards=cards)}


async def generate_quiz_node(state: CardReviewState, config: RunnableConfig) -> CardReviewState:
    """根据知识卡片生成练习题。"""
    if state.get("errors"):
        return {}

    cards = state["cards"]
    prompt = (
        QUIZ_GENERATION_PROMPT.format(
            cards=cards.model_dump_json(indent=2, exclude_none=True)
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
) -> CardReviewState:
    """根据知识点生成初始复习计划。"""
    if state.get("errors"):
        return {}

    weak_points = state.get("knowledge_points", [])[:5]
    prompt = REVIEW_PLAN_PROMPT.format(
        weak_points=json.dumps(weak_points, ensure_ascii=False, indent=2),
        wrong_answers="[]",
    ) + """
请输出 JSON，格式为：
{"weak_points":[],"tasks":[{"day":1,"topic":"","task":"","reason":"","is_completed":false}]}
"""
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


async def format_result_node(state: CardReviewState, config: RunnableConfig) -> CardReviewState:
    """整理知识卡片、题目和复习计划，输出适合前端展示的 Markdown。"""
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
        f"### Day {task.day}: {task.topic}\n"
        f"- 任务：{task.task}\n"
        f"- 原因：{task.reason}"
        for task in review_plan.tasks
    ]

    content = "\n\n".join(
        [
            f"# 知识卡片与复习计划：{state.get('topic', '学习资料')}",
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


agent = StateGraph(CardReviewState)
agent.add_node("parse_input_node", parse_input_node)
agent.add_node("extract_knowledge_node", extract_knowledge_node)
agent.add_node("generate_cards_node", generate_cards_node)
agent.add_node("generate_quiz_node", generate_quiz_node)
agent.add_node("generate_review_plan_node", generate_review_plan_node)
agent.add_node("format_result_node", format_result_node)

agent.set_entry_point("parse_input_node")
agent.add_edge("parse_input_node", "extract_knowledge_node")
agent.add_edge("extract_knowledge_node", "generate_cards_node")
agent.add_edge("generate_cards_node", "generate_quiz_node")
agent.add_edge("generate_quiz_node", "generate_review_plan_node")
agent.add_edge("generate_review_plan_node", "format_result_node")
agent.add_edge("format_result_node", END)

card_review_agent = agent.compile()
