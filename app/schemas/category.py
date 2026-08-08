"""分类 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """创建分类入参。"""

    name: str = Field(..., min_length=1, max_length=50, description="分类名")
    description: str | None = Field(None, max_length=200, description="描述")
    # slug 可选：不传则自动按拼音生成
    slug: str | None = Field(None, max_length=50, description="拼音别名")


class CategoryUpdate(BaseModel):
    """更新分类入参（字段均可选）。"""

    name: str | None = Field(None, min_length=1, max_length=50, description="分类名")
    description: str | None = Field(None, max_length=200, description="描述")
    slug: str | None = Field(None, max_length=50, description="拼音别名（空则按名称生成）")


class CategoryOut(BaseModel):
    """分类出参。"""

    id: int
    name: str
    slug: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
