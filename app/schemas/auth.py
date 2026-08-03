"""认证与用户 Schema。"""
from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    """登录入参（用户名或邮箱 + 密码）。"""

    user_info: str = Field(..., min_length=1, max_length=255, description="用户名或邮箱")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class RegisterIn(BaseModel):
    """注册入参。"""

    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserOut(BaseModel):
    """用户出参（不含密码）。"""

    id: int
    email: str
    user_name: str | None = None
    role: int


class TokenOut(BaseModel):
    """登录成功返回的令牌。"""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
