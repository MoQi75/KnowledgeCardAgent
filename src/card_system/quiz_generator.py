"""测验题生成业务骨架。"""

from schema.card import KnowledgeCardList
from schema.quiz import QuizQuestionList


async def generate_quiz(cards: KnowledgeCardList) -> QuizQuestionList:
    """根据知识卡片生成练习题，具体 LLM 调用在后续阶段实现。"""
    raise NotImplementedError("Quiz generation will be implemented in a later stage.")
