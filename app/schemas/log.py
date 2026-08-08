"""操作日志 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogOut(BaseModel):
    """日志出参。"""

    id: int
    created: datetime
    user_id: int | None = None
    username: str | None = None
    action: str
    method: str
    path: str
    status: int
    ms: int
    ip: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LogListResult(BaseModel):
    """日志分页结果。"""

    items: list[LogOut]
    total: int
    page: int
    page_size: int
    total_page: int
