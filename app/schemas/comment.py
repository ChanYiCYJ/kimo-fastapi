"""评论 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    """提交评论入参（需登录）。"""

    article_id: int = Field(..., description="文章 id")
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")


class CommentStatusUpdate(BaseModel):
    """审核状态更新入参。"""

    status: int = Field(..., ge=0, le=2, description="0=待审核, 1=已通过, 2=已拒绝")


class CommentOut(BaseModel):
    """评论出参。"""

    id: int
    article_id: int
    user_id: int | None = None
    username: str | None = None
    content: str
    status: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentListResult(BaseModel):
    """评论分页结果。"""

    items: list[CommentOut]
    total: int
    page: int
    page_size: int
    total_page: int
