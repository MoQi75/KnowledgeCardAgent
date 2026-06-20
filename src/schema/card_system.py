from pydantic import BaseModel, Field

from schema.card import KnowledgeCardList
from schema.quiz import AnswerCheckResult, AnswerSubmission, QuizQuestionList
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

