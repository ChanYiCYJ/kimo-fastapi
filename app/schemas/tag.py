"""标签 Schema。"""
from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    """创建标签入参。"""

    tag_name: str = Field(..., min_length=1, max_length=50, description="标签名")


class TagOut(BaseModel):
    """标签出参。"""

    id: int
    tag_name: str

    model_config = ConfigDict(from_attributes=True)
