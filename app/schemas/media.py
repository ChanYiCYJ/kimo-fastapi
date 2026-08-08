"""媒体 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MediaOut(BaseModel):
    """媒体出参。"""

    id: int
    filename: str
    original_name: str | None = None
    url: str
    size: int
    mime: str | None = None
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class MediaListResult(BaseModel):
    """媒体分页结果。"""

    items: list[MediaOut]
    total: int
    page: int
    page_size: int
    total_page: int
