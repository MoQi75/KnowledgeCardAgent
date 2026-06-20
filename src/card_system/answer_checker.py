"""答案批改业务骨架。"""

from schema.quiz import AnswerCheckResult, AnswerSubmission, QuizQuestion


async def check_answer(
    question: QuizQuestion, submission: AnswerSubmission
) -> AnswerCheckResult:
    """批改用户答案，具体评分逻辑在后续阶段实现。"""
    raise NotImplementedError("Answer checking will be implemented in a later stage.")

