"""复习计划生成业务。"""

from schema.review import ReviewPlan, ReviewTask


async def generate_review_plan(weak_points: list[str]) -> ReviewPlan:
    """根据薄弱点生成默认三阶段复习计划。"""
    points = [point for point in weak_points if point.strip()] or ["本次学习资料"]
    tasks = [
        ReviewTask(
            day=index + 1,
            topic=point[:80],
            task="复习相关知识卡片，完成对应练习题，并记录仍不熟悉的概念。",
            reason="该知识点被标记为薄弱点，需要优先巩固。",
        )
        for index, point in enumerate(points[:7])
    ]
    return ReviewPlan(weak_points=points, tasks=tasks)
