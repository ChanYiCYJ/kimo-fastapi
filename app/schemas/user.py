"""用户管理 Schema（管理员操作）。"""
from pydantic import BaseModel, Field


class UserRoleUpdate(BaseModel):
    """角色更新入参。"""

    role: int = Field(..., ge=0, le=1, description="0=管理员, 1=普通用户")
