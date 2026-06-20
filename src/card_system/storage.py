"""知识卡片系统存储层骨架。"""

from schema.review import StudySummary


async def get_study_summary() -> StudySummary:
    """获取学习统计摘要，具体存储实现留到后续阶段。"""
    raise NotImplementedError("Storage will be implemented in a later stage.")

