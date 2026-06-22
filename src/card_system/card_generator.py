"""知识卡片生成业务骨架。"""

from schema.card import KnowledgeCardList


async def generate_cards(document_id: str, source_text: str) -> KnowledgeCardList:
    """根据文档内容生成知识卡片，具体 LLM 调用在后续阶段实现。"""
    raise NotImplementedError("Card generation will be implemented in a later stage.")
