"""知识卡片系统的 PostgreSQL 持久化层。"""

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv

from schema.card import KnowledgeCard, KnowledgeCardList
from schema.quiz import AnswerCheckResult, AnswerSubmission, QuizQuestion, QuizQuestionList
from schema.review import ReviewPlan, StudySummary

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class CardSystemStorageError(RuntimeError):
    """知识卡片系统存储层错误。"""


def _load_env() -> None:
    env_file = find_dotenv(usecwd=True)
    if env_file:
        load_dotenv(env_file, override=False)


def _require_postgres_config() -> dict[str, str]:
    _load_env()
    required = {
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "dbname": os.getenv("POSTGRES_DB"),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        env_names = {
            "user": "POSTGRES_USER",
            "password": "POSTGRES_PASSWORD",
            "host": "POSTGRES_HOST",
            "port": "POSTGRES_PORT",
            "dbname": "POSTGRES_DB",
        }
        missing_names = ", ".join(env_names[key] for key in missing)
        raise CardSystemStorageError(
            f"Missing PostgreSQL configuration: {missing_names}. "
            "Set these environment variables before using card system storage."
        )
    return {key: str(value) for key, value in required.items()}


async def _connect():
    """延迟导入 psycopg，确保数据库不可用时模块 import 不失败。"""
    try:
        from psycopg import AsyncConnection
        from psycopg.rows import dict_row
    except ImportError as e:
        raise CardSystemStorageError(
            "psycopg is required for card system storage. Install project dependencies first."
        ) from e

    try:
        return await AsyncConnection.connect(**_require_postgres_config(), row_factory=dict_row)
    except Exception as e:
        raise CardSystemStorageError(f"Unable to connect to PostgreSQL: {e}") from e


def _schema_sql() -> str:
    return (Path(__file__).with_name("db_schema.sql")).read_text(encoding="utf-8")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


async def init_card_system_db() -> None:
    """初始化知识卡片系统所需的数据表。"""
    async with await _connect() as conn:
        await conn.execute(_schema_sql())
        await conn.commit()


async def create_document(
    title: str,
    content: str,
    file_path: str | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """创建学习资料记录。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO documents (user_id, title, content, file_path)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (user_id, title, content, file_path),
            )
            row = await cur.fetchone()
        await conn.commit()
    return dict(row)


async def list_documents(user_id: str = DEFAULT_USER_ID) -> list[dict[str, Any]]:
    """列出用户的学习资料。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT *
                FROM documents
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = await cur.fetchall()
    return [dict(row) for row in rows]


async def get_document(document_id: str) -> dict[str, Any] | None:
    """按 ID 获取学习资料。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


def _normalize_cards(cards: KnowledgeCardList | Sequence[KnowledgeCard]) -> list[KnowledgeCard]:
    if isinstance(cards, KnowledgeCardList):
        return cards.cards
    return list(cards)


async def save_knowledge_cards(
    document_id: str, cards: KnowledgeCardList | Sequence[KnowledgeCard]
) -> list[dict[str, Any]]:
    """保存知识卡片。"""
    saved: list[dict[str, Any]] = []
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            for card in _normalize_cards(cards):
                await cur.execute(
                    """
                    INSERT INTO knowledge_cards (
                        id, document_id, title, summary, keywords, explanation, example,
                        common_mistakes, related_concepts, source_text, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        summary = EXCLUDED.summary,
                        keywords = EXCLUDED.keywords,
                        explanation = EXCLUDED.explanation,
                        example = EXCLUDED.example,
                        common_mistakes = EXCLUDED.common_mistakes,
                        related_concepts = EXCLUDED.related_concepts,
                        source_text = EXCLUDED.source_text
                    RETURNING *
                    """,
                    (
                        card.id,
                        document_id,
                        card.title,
                        card.summary,
                        _json(card.keywords),
                        card.explanation,
                        card.example,
                        _json(card.common_mistakes),
                        _json(card.related_concepts),
                        card.source_text,
                        card.created_at,
                    ),
                )
                row = await cur.fetchone()
                saved.append(dict(row))
        await conn.commit()
    return saved


async def list_knowledge_cards(document_id: str | None = None) -> list[dict[str, Any]]:
    """列出知识卡片，可按文档过滤。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            if document_id:
                await cur.execute(
                    """
                    SELECT *
                    FROM knowledge_cards
                    WHERE document_id = %s
                    ORDER BY created_at DESC
                    """,
                    (document_id,),
                )
            else:
                await cur.execute("SELECT * FROM knowledge_cards ORDER BY created_at DESC")
            rows = await cur.fetchall()
    return [dict(row) for row in rows]


def _normalize_questions(
    questions: QuizQuestionList | Sequence[QuizQuestion],
) -> list[QuizQuestion]:
    if isinstance(questions, QuizQuestionList):
        return questions.questions
    return list(questions)


async def save_quiz_questions(
    questions: QuizQuestionList | Sequence[QuizQuestion],
) -> list[dict[str, Any]]:
    """保存练习题。"""
    saved: list[dict[str, Any]] = []
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            for question in _normalize_questions(questions):
                await cur.execute(
                    """
                    INSERT INTO quiz_questions (
                        id, card_id, question_type, question, options, answer,
                        explanation, difficulty, related_card_title
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        question_type = EXCLUDED.question_type,
                        question = EXCLUDED.question,
                        options = EXCLUDED.options,
                        answer = EXCLUDED.answer,
                        explanation = EXCLUDED.explanation,
                        difficulty = EXCLUDED.difficulty,
                        related_card_title = EXCLUDED.related_card_title
                    RETURNING *
                    """,
                    (
                        question.id,
                        question.card_id,
                        question.question_type,
                        question.question,
                        _json(question.options),
                        question.answer,
                        question.explanation,
                        question.difficulty,
                        question.related_card_title,
                    ),
                )
                row = await cur.fetchone()
                saved.append(dict(row))
        await conn.commit()
    return saved


async def list_quiz_questions(card_id: str | None = None) -> list[dict[str, Any]]:
    """列出练习题，可按知识卡片过滤。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            if card_id:
                await cur.execute(
                    """
                    SELECT *
                    FROM quiz_questions
                    WHERE card_id = %s
                    ORDER BY created_at DESC
                    """,
                    (card_id,),
                )
            else:
                await cur.execute("SELECT * FROM quiz_questions ORDER BY created_at DESC")
            rows = await cur.fetchall()
    return [dict(row) for row in rows]


async def save_answer_record(
    submission: AnswerSubmission,
    result: AnswerCheckResult,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """保存答题记录；答错时同步更新错题表。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO answer_records (
                    user_id, question_id, user_answer, is_correct, score, feedback
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    user_id,
                    submission.question_id,
                    submission.user_answer,
                    result.is_correct,
                    result.score,
                    result.feedback,
                ),
            )
            row = await cur.fetchone()

            if not result.is_correct:
                await cur.execute(
                    """
                    INSERT INTO wrong_questions (
                        user_id, question_id, related_knowledge, error_count, last_wrong_at
                    )
                    VALUES (%s, %s, %s, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, question_id) DO UPDATE SET
                        related_knowledge = EXCLUDED.related_knowledge,
                        error_count = wrong_questions.error_count + 1,
                        last_wrong_at = CURRENT_TIMESTAMP
                    """,
                    (user_id, submission.question_id, result.weak_point),
                )
        await conn.commit()
    return dict(row)


async def list_wrong_questions(user_id: str = DEFAULT_USER_ID) -> list[dict[str, Any]]:
    """列出用户错题。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT w.*, q.question, q.answer, q.explanation
                FROM wrong_questions w
                JOIN quiz_questions q ON q.id = w.question_id
                WHERE w.user_id = %s
                ORDER BY w.error_count DESC, w.last_wrong_at DESC
                """,
                (user_id,),
            )
            rows = await cur.fetchall()
    return [dict(row) for row in rows]


async def save_review_plan(
    plan: ReviewPlan,
    title: str = "知识卡片复习计划",
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """保存复习计划和计划中的每日任务。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO review_plans (id, user_id, title, weak_points, created_at)
                VALUES (%s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    weak_points = EXCLUDED.weak_points
                RETURNING *
                """,
                (plan.id, user_id, title, _json(plan.weak_points), plan.created_at),
            )
            row = await cur.fetchone()

            await cur.execute("DELETE FROM review_tasks WHERE plan_id = %s", (plan.id,))
            for task in plan.tasks:
                await cur.execute(
                    """
                    INSERT INTO review_tasks (plan_id, day, topic, task, reason, is_completed)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        plan.id,
                        task.day,
                        task.topic,
                        task.task,
                        task.reason,
                        task.is_completed,
                    ),
                )
        await conn.commit()
    return dict(row)


async def get_study_summary(user_id: str = DEFAULT_USER_ID) -> StudySummary:
    """统计用户学习数据。"""
    async with await _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM documents WHERE user_id = %s) AS document_count,
                    (
                        SELECT COUNT(*)
                        FROM knowledge_cards kc
                        JOIN documents d ON d.id = kc.document_id
                        WHERE d.user_id = %s
                    ) AS card_count,
                    (
                        SELECT COUNT(*)
                        FROM quiz_questions q
                        JOIN knowledge_cards kc ON kc.id = q.card_id
                        JOIN documents d ON d.id = kc.document_id
                        WHERE d.user_id = %s
                    ) AS quiz_count,
                    (SELECT COUNT(*) FROM answer_records WHERE user_id = %s) AS answer_count,
                    (
                        SELECT COUNT(*)
                        FROM answer_records
                        WHERE user_id = %s AND is_correct = false
                    ) AS wrong_count
                """,
                (user_id, user_id, user_id, user_id, user_id),
            )
            row = await cur.fetchone()

    answer_count = int(row["answer_count"] or 0)
    wrong_count = int(row["wrong_count"] or 0)
    accuracy = 0 if answer_count == 0 else (answer_count - wrong_count) / answer_count
    return StudySummary(
        document_count=int(row["document_count"] or 0),
        card_count=int(row["card_count"] or 0),
        quiz_count=int(row["quiz_count"] or 0),
        answer_count=answer_count,
        wrong_count=wrong_count,
        accuracy=accuracy,
    )
