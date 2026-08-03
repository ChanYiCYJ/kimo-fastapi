"""页面 Schema。"""
from pydantic import BaseModel, ConfigDict, Field


class PageCreate(BaseModel):
    """创建页面入参。"""

    name: str = Field(..., min_length=1, max_length=100, description="页面名称")
    content: str | None = Field(None, description="内容")
    type: str = Field("markdown", pattern="^(markdown|html|list|link)$", description="页面类型")
    status: int = Field(0, description="状态")


class PageUpdate(BaseModel):
    """更新页面入参。"""

    name: str | None = Field(None, min_length=1, max_length=100, description="页面名称")
    content: str | None = Field(None, description="内容")
    type: str | None = Field(None, pattern="^(markdown|html|list|link)$", description="页面类型")
    status: int | None = Field(None, description="状态")


class PageOut(BaseModel):
    """页面出参。"""

    id: int
    name: str
    content: str | None = None
    type: str
    status: int

    model_config = ConfigDict(from_attributes=True)
