"""通用响应模型：统一接口返回格式。"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应结构。

    约定：code=0 表示成功；data 为业务数据；message 为提示信息。
    """

    code: int = 0
    message: str = "ok"
    data: T | None = None
