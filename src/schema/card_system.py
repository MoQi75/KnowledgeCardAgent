from typing import Any

from pydantic import BaseModel, Field

from schema.card import KnowledgeCardList
from schema.quiz import AnswerCheckResult, QuizQuestionList
from schema.review import ReviewPlan, StudySummary


class CreateDocumentRequest(BaseModel):
    """创建学习资料请求。"""

    title: str | None = Field(default=None, description="资料标题")
    content: str = Field(description="学习资料文本内容")
    file_path: str | None = Field(default=None, description="可选文件路径")


class GenerateCardsRequest(BaseModel):
    """生成知识卡片请求。"""

    document_id: str | None = Field(default=None, description="已有资料 ID")
    text: str | None = Field(default=None, description="直接输入的学习资料文本")
    title: str | None = Field(default=None, description="直接输入文本的资料标题")


class GenerateCardsResponse(BaseModel):
    """生成知识卡片响应。"""

    document: dict
    cards: KnowledgeCardList


class GenerateQuizRequest(BaseModel):
    """生成题目请求。"""

    card_id: str | None = Field(default=None, description="可选知识卡片 ID")


class GenerateQuizResponse(BaseModel):
    """生成题目响应。"""

    questions: QuizQuestionList


class SubmitAnswerResponse(BaseModel):
    """提交答案响应。"""

    result: AnswerCheckResult
    record: dict


class GenerateReviewPlanRequest(BaseModel):
    """生成复习计划请求。"""

    weak_points: list[str] | None = Field(default=None, description="可选薄弱点列表")
    title: str | None = Field(default=None, description="复习计划标题")


class GenerateReviewPlanResponse(BaseModel):
    """生成复习计划响应。"""

    plan: ReviewPlan
    record: dict


class StudySummaryResponse(StudySummary):
    """学习统计响应。"""


class AgentTraceItem(BaseModel):
    """CardReviewAgent 前端执行过程展示项。"""

    step: int = Field(ge=1, description="执行步骤序号")
    name: str = Field(description="步骤名称")
    status: str = Field(description="执行状态")
    detail: str = Field(description="步骤说明")


class AnalyzeFileResponse(BaseModel):
    """上传学习资料后的智能体分析响应。"""

    document_id: str
    agent_name: str = Field(default="CardReviewAgent")
    agent_trace: list[AgentTraceItem]
    cards: list[dict[str, Any]]
    quizzes: list[dict[str, Any]]
    review_plan: dict[str, Any]
    summary: dict[str, Any]
