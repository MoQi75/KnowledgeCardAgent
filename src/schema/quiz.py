from uuid import uuid4

from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """围绕知识卡片生成的练习题。"""

    id: str = Field(default_factory=lambda: str(uuid4()), description="题目 ID")
    card_id: str = Field(description="关联知识卡片 ID")
    question_type: str = Field(description="题型，例如 single_choice、true_false、short_answer")
    question: str = Field(description="题干")
    options: list[str] = Field(default_factory=list, description="选项列表")
    answer: str = Field(description="标准答案")
    explanation: str = Field(description="答案解析")
    difficulty: str = Field(default="medium", description="难度：easy、medium、hard")
    related_card_title: str = Field(description="关联知识卡片标题")


class QuizQuestionList(BaseModel):
    """练习题集合。"""

    questions: list[QuizQuestion] = Field(default_factory=list, description="练习题列表")


class AnswerSubmission(BaseModel):
    """用户提交的答题内容。"""

    question_id: str = Field(description="题目 ID")
    user_answer: str = Field(description="用户答案")


class AnswerCheckResult(BaseModel):
    """答案批改结果。"""

    question_id: str = Field(description="题目 ID")
    is_correct: bool = Field(description="是否正确")
    score: float = Field(ge=0, le=1, description="得分，范围 0 到 1")
    feedback: str = Field(description="面向用户的批改反馈")
    correct_answer: str = Field(description="正确答案")
    explanation: str = Field(description="解析")
    weak_point: str = Field(default="", description="暴露出的薄弱点")

