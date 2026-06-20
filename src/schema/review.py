from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """统一生成带时区的创建时间。"""
    return datetime.now(timezone.utc)


class ReviewTask(BaseModel):
    """单日复习任务。"""

    day: int = Field(ge=1, description="第几天")
    topic: str = Field(description="复习主题")
    task: str = Field(description="具体复习任务")
    reason: str = Field(description="安排该任务的原因")
    is_completed: bool = Field(default=False, description="是否完成")


class ReviewPlan(BaseModel):
    """基于薄弱点生成的复习计划。"""

    id: str = Field(default_factory=lambda: str(uuid4()), description="复习计划 ID")
    weak_points: list[str] = Field(default_factory=list, description="薄弱点列表")
    tasks: list[ReviewTask] = Field(default_factory=list, description="复习任务列表")
    created_at: datetime = Field(default_factory=utc_now, description="创建时间")


class StudySummary(BaseModel):
    """学习数据统计摘要。"""

    document_count: int = Field(default=0, ge=0, description="文档数量")
    card_count: int = Field(default=0, ge=0, description="知识卡片数量")
    quiz_count: int = Field(default=0, ge=0, description="题目数量")
    answer_count: int = Field(default=0, ge=0, description="答题次数")
    wrong_count: int = Field(default=0, ge=0, description="错误次数")
    accuracy: float = Field(default=0, ge=0, le=1, description="正确率")

