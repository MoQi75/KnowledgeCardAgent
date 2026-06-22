"""答案批改业务。"""

import re

from schema.quiz import AnswerCheckResult, AnswerSubmission, QuizQuestion


async def check_answer(question: QuizQuestion, submission: AnswerSubmission) -> AnswerCheckResult:
    """使用轻量规则批改答案，后续可替换为 LLM 语义批改。"""
    expected = _normalize(question.answer)
    actual = _normalize(submission.user_answer)
    is_correct = bool(actual) and (actual == expected or actual in expected or expected in actual)
    score = 1.0 if is_correct else 0.0
    weak_point = "" if is_correct else question.related_card_title

    return AnswerCheckResult(
        question_id=submission.question_id,
        is_correct=is_correct,
        score=score,
        feedback="回答正确。" if is_correct else "回答不完整或不正确，请复习对应知识卡片。",
        correct_answer=question.answer,
        explanation=question.explanation,
        weak_point=weak_point,
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower())
