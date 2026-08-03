"""文章 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagOut


class ArticleCreate(BaseModel):
    """创建文章入参。"""

    title: str = Field(..., min_length=1, description="标题")
    content: str = Field(..., min_length=1, description="Markdown 内容")
    description: str | None = Field(None, description="摘要")
    cover_image: str | None = Field(None, description="封面图 URL")
    category_id: int | None = Field(None, description="分类 ID")
    tags: list[str] = Field(default_factory=list, description="标签名列表")


class ArticleUpdate(BaseModel):
    """更新文章入参（全部可选）。"""

    title: str | None = Field(None, min_length=1, description="标题")
    content: str | None = Field(None, description="Markdown 内容")
    description: str | None = Field(None, description="摘要")
    cover_image: str | None = Field(None, description="封面图 URL")
    category_id: int | None = Field(None, description="分类 ID")
    tags: list[str] | None = Field(None, description="标签名列表")


class ArticleListItem(BaseModel):
    """文章列表项（不含正文，含分类名与标签）。"""

    id: int
    title: str
    description: str | None = None
    cover_image: str | None = None
    created: datetime
    category_id: int | None = None
    category_name: str | None = None
    tags: list[TagOut] = []


class ArticleOut(BaseModel):
    """文章详情出参。"""

    id: int
    title: str
    content: str
    content_html: str = ""
    description: str | None = None
    cover_image: str | None = None
    created: datetime
    category_id: int | None = None
    category_name: str | None = None
    tags: list[TagOut] = []

    model_config = ConfigDict(from_attributes=True)
