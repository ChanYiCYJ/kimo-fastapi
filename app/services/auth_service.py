"""认证业务：登录、注册。"""
from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.crud.user import user as user_crud
from app.models.user import UserInfo
from app.services.init_service import is_register_allowed


async def authenticate(user_info: str, password: str) -> UserInfo | None:
    """按用户名/邮箱校验密码，成功返回用户，失败返回 None。"""
    db_user = await user_crud.get_by_name_or_email(user_info)
    if not db_user or not verify_password(password, db_user.password):
        return None
    return db_user


async def login(user_info: str, password: str) -> dict:
    """登录：校验身份并签发 JWT。"""
    db_user = await authenticate(user_info, password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user_id=db_user.id, role=db_user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "user_name": db_user.user_name,
            "role": db_user.role,
        },
    }


async def register(username: str, email: str, password: str) -> dict:
    """注册普通用户（role=1），密码做哈希存储。

    注意：
    - 注册创建的账户一律为普通用户（role=1），【不会】成为管理员；
      管理员由启动时的 ensure_default_admin() 自动创建，或手动将库中 role 置 0。
    - 若站点关闭了开放注册（allow_register=0 或 ALLOW_REGISTER=False），将拒绝注册。
    """
    if not await is_register_allowed():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前站点未开放注册，请联系管理员",
        )
    if await user_crud.get_by_username(username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if await user_crud.get_by_email(email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    db_user = await user_crud.create(
        {
            "user_name": username,
            "email": email,
            "password": hash_password(password),
            "role": 1,
        }
    )
    return {
        "id": db_user.id,
        "email": db_user.email,
        "user_name": db_user.user_name,
        "role": db_user.role,
    }
