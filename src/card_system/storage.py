"""Knowledge card system persistence layer backed by MySQL."""

import json
import os
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import find_dotenv, load_dotenv

from schema.card import KnowledgeCard, KnowledgeCardList
from schema.quiz import AnswerCheckResult, AnswerSubmission, QuizQuestion, QuizQuestionList
from schema.review import ReviewPlan, StudySummary

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class CardSystemStorageError(RuntimeError):
    """Raised when the knowledge card storage layer cannot complete an operation."""


def _load_env() -> None:
    env_file = find_dotenv(usecwd=True)
    if env_file:
        load_dotenv(env_file, override=False)


def _require_mysql_config() -> dict[str, Any]:
    _load_env()
    required = {
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "host": os.getenv("MYSQL_HOST"),
        "port": os.getenv("MYSQL_PORT"),
        "db": os.getenv("MYSQL_DATABASE"),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        env_names = {
            "user": "MYSQL_USER",
            "password": "MYSQL_PASSWORD",
            "host": "MYSQL_HOST",
            "port": "MYSQL_PORT",
            "db": "MYSQL_DATABASE",
        }
        missing_names = ", ".join(env_names[key] for key in missing)
        raise CardSystemStorageError(
            f"Missing MySQL configuration: {missing_names}. "
            "Set these environment variables before using card system storage."
        )

    config: dict[str, Any] = {key: str(value) for key, value in required.items()}
    config["port"] = int(config["port"])
    return config


@asynccontextmanager
async def _connect() -> AsyncIterator[Any]:
    """Delay importing aiomysql so module import still works without a database driver."""
    try:
        import aiomysql
    except ImportError as e:
        raise CardSystemStorageError(
            "aiomysql is required for MySQL card system storage. Install project dependencies first."
        ) from e

    try:
        conn = await aiomysql.connect(
            **_require_mysql_config(),
            charset="utf8mb4",
            autocommit=False,
            cursorclass=aiomysql.DictCursor,
        )
    except Exception as e:
        raise CardSystemStorageError(f"Unable to connect to MySQL: {e}") from e

    try:
        yield conn
    finally:
        conn.close()
        await conn.ensure_closed()


def _schema_sql() -> str:
    return (Path(__file__).with_name("db_schema.sql")).read_text(encoding="utf-8")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


JSON_FIELDS = {"keywords", "common_mistakes", "related_concepts", "options", "weak_points"}


def _decode_json_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    for field in JSON_FIELDS & normalized.keys():
        normalized[field] = _decode_json_value(normalized[field])
    return normalized


def _new_id() -> str:
    return str(uuid4())


async def _fetch_one(conn: Any, query: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        row = await cur.fetchone()
    return _normalize_row(dict(row)) if row else None


async def _execute_schema(conn: Any, schema: str) -> None:
    async with conn.cursor() as cur:
        statements = [statement.strip() for statement in schema.split(";") if statement.strip()]
        for statement in statements:
            await cur.execute(statement)


async def init_card_system_db() -> None:
    """Initialize all tables required by the knowledge card system."""
    async with _connect() as conn:
        await _execute_schema(conn, _schema_sql())
        await conn.commit()


async def create_document(
    title: str,
    content: str,
    file_path: str | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """Create a learning material record."""
    document_id = _new_id()
    async with _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO documents (id, user_id, title, content, file_path)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (document_id, user_id, title, content, file_path),
            )
        await conn.commit()
        document = await _fetch_one(conn, "SELECT * FROM documents WHERE id = %s", (document_id,))
    if not document:
        raise CardSystemStorageError("Failed to create document.")
    return document


async def list_documents(user_id: str = DEFAULT_USER_ID) -> list[dict[str, Any]]:
    """List learning materials for a user."""
    async with _connect() as conn:
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
    return [_normalize_row(dict(row)) for row in rows]


async def get_document(document_id: str) -> dict[str, Any] | None:
    """Get a learning material by ID."""
    async with _connect() as conn:
        return await _fetch_one(conn, "SELECT * FROM documents WHERE id = %s", (document_id,))


def _normalize_cards(cards: KnowledgeCardList | Sequence[KnowledgeCard]) -> list[KnowledgeCard]:
    if isinstance(cards, KnowledgeCardList):
        return cards.cards
    return list(cards)


async def save_knowledge_cards(
    document_id: str, cards: KnowledgeCardList | Sequence[KnowledgeCard]
) -> list[dict[str, Any]]:
    """Save generated knowledge cards."""
    saved: list[dict[str, Any]] = []
    async with _connect() as conn:
        async with conn.cursor() as cur:
            for card in _normalize_cards(cards):
                await cur.execute(
                    """
                    INSERT INTO knowledge_cards (
                        id, document_id, title, summary, keywords, explanation, example,
                        common_mistakes, related_concepts, source_text, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        title = VALUES(title),
                        summary = VALUES(summary),
                        keywords = VALUES(keywords),
                        explanation = VALUES(explanation),
                        example = VALUES(example),
                        common_mistakes = VALUES(common_mistakes),
                        related_concepts = VALUES(related_concepts),
                        source_text = VALUES(source_text)
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
        await conn.commit()
        for card in _normalize_cards(cards):
            row = await _fetch_one(conn, "SELECT * FROM knowledge_cards WHERE id = %s", (card.id,))
            if row:
                saved.append(row)
    return saved


async def list_knowledge_cards(document_id: str | None = None) -> list[dict[str, Any]]:
    """List knowledge cards, optionally filtered by document ID."""
    async with _connect() as conn:
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
    return [_normalize_row(dict(row)) for row in rows]


def _normalize_questions(
    questions: QuizQuestionList | Sequence[QuizQuestion],
) -> list[QuizQuestion]:
    if isinstance(questions, QuizQuestionList):
        return questions.questions
    return list(questions)


async def save_quiz_questions(
    questions: QuizQuestionList | Sequence[QuizQuestion],
) -> list[dict[str, Any]]:
    """Save generated quiz questions."""
    saved: list[dict[str, Any]] = []
    async with _connect() as conn:
        async with conn.cursor() as cur:
            for question in _normalize_questions(questions):
                await cur.execute(
                    """
                    INSERT INTO quiz_questions (
                        id, card_id, question_type, question, options, answer,
                        explanation, difficulty, related_card_title
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        question_type = VALUES(question_type),
                        question = VALUES(question),
                        options = VALUES(options),
                        answer = VALUES(answer),
                        explanation = VALUES(explanation),
                        difficulty = VALUES(difficulty),
                        related_card_title = VALUES(related_card_title)
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
        await conn.commit()
        for question in _normalize_questions(questions):
            row = await _fetch_one(
                conn, "SELECT * FROM quiz_questions WHERE id = %s", (question.id,)
            )
            if row:
                saved.append(row)
    return saved


async def list_quiz_questions(card_id: str | None = None) -> list[dict[str, Any]]:
    """List quiz questions, optionally filtered by card ID."""
    async with _connect() as conn:
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
    return [_normalize_row(dict(row)) for row in rows]


async def save_answer_record(
    submission: AnswerSubmission,
    result: AnswerCheckResult,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """Save an answer record and update wrong-question memory when needed."""
    record_id = _new_id()
    async with _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO answer_records (
                    id, user_id, question_id, user_answer, is_correct, score, feedback
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    record_id,
                    user_id,
                    submission.question_id,
                    submission.user_answer,
                    result.is_correct,
                    result.score,
                    result.feedback,
                ),
            )

            if not result.is_correct:
                await cur.execute(
                    """
                    INSERT INTO wrong_questions (
                        id, user_id, question_id, related_knowledge, error_count, last_wrong_at
                    )
                    VALUES (%s, %s, %s, %s, 1, CURRENT_TIMESTAMP)
                    ON DUPLICATE KEY UPDATE
                        related_knowledge = VALUES(related_knowledge),
                        error_count = error_count + 1,
                        last_wrong_at = CURRENT_TIMESTAMP
                    """,
                    (_new_id(), user_id, submission.question_id, result.weak_point),
                )
        await conn.commit()
        record = await _fetch_one(conn, "SELECT * FROM answer_records WHERE id = %s", (record_id,))
    if not record:
        raise CardSystemStorageError("Failed to save answer record.")
    return record


async def list_wrong_questions(user_id: str = DEFAULT_USER_ID) -> list[dict[str, Any]]:
    """List wrong questions for a user."""
    async with _connect() as conn:
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
    return [_normalize_row(dict(row)) for row in rows]


async def save_review_plan(
    plan: ReviewPlan,
    title: str = "知识卡片复习计划",
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """Save a review plan and its daily tasks."""
    async with _connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO review_plans (id, user_id, title, weak_points, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    weak_points = VALUES(weak_points)
                """,
                (plan.id, user_id, title, _json(plan.weak_points), plan.created_at),
            )

            await cur.execute("DELETE FROM review_tasks WHERE plan_id = %s", (plan.id,))
            for task in plan.tasks:
                await cur.execute(
                    """
                    INSERT INTO review_tasks (
                        id, plan_id, day, topic, task, reason, is_completed
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        _new_id(),
                        plan.id,
                        task.day,
                        task.topic,
                        task.task,
                        task.reason,
                        task.is_completed,
                    ),
                )
        await conn.commit()
        record = await _fetch_one(conn, "SELECT * FROM review_plans WHERE id = %s", (plan.id,))
    if not record:
        raise CardSystemStorageError("Failed to save review plan.")
    return record


async def get_study_summary(user_id: str = DEFAULT_USER_ID) -> StudySummary:
    """Aggregate user learning statistics."""
    async with _connect() as conn:
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
                        WHERE user_id = %s AND is_correct = 0
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
