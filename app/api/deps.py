"""依赖注入：JWT 认证。

- `CurrentUser`：已登录用户
- `CurrentAdmin`：管理员（role=0，对应 Kimo 的 dashboard 权限）
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.crud.user import user as user_crud
from app.models.user import UserInfo

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
) -> UserInfo:
    """从 Bearer Token 解析当前用户。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_crud.get(int(payload["sub"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[UserInfo, Depends(get_current_user)]


async def get_current_admin(current_user: CurrentUser) -> UserInfo:
    """管理员权限（role=0）。"""
    if current_user.role != 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


CurrentAdmin = Annotated[UserInfo, Depends(get_current_admin)]
