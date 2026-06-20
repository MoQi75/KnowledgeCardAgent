from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """统一生成带时区的创建时间。"""
    return datetime.now(timezone.utc)


class KnowledgeCard(BaseModel):
    """从文档中抽取出的单张知识卡片。"""

    id: str = Field(default_factory=lambda: str(uuid4()), description="知识卡片 ID")
    document_id: str = Field(description="来源文档 ID")
    title: str = Field(description="知识点标题")
    summary: str = Field(description="知识点摘要")
    keywords: list[str] = Field(default_factory=list, description="关键词列表")
    explanation: str = Field(description="详细解释")
    example: str = Field(default="", description="辅助理解的例子")
    common_mistakes: list[str] = Field(default_factory=list, description="常见误区")
    related_concepts: list[str] = Field(default_factory=list, description="相关概念")
    source_text: str = Field(description="支撑该卡片的原文片段")
    created_at: datetime = Field(default_factory=utc_now, description="创建时间")


class KnowledgeCardList(BaseModel):
    """知识卡片集合。"""

    cards: list[KnowledgeCard] = Field(default_factory=list, description="知识卡片列表")

