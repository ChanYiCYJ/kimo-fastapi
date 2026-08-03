"""安全模块：JWT 令牌与密码哈希。

密码哈希使用 werkzeug（与 Kimo 原项目一致），
保证现有 userinfo 表中的历史密码仍可验证。
"""
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.config import settings


# ---------- 密码哈希 ----------
def hash_password(password: str) -> str:
    """生成密码哈希。"""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码（兼容 Kimo 原项目的哈希格式）。"""
    return check_password_hash(password_hash, password)


# ---------- JWT ----------
def create_access_token(
    user_id: int,
    role: int,
    expires_minutes: int | None = None,
) -> str:
    """生成 JWT 访问令牌。"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解析 JWT，失败返回 None。"""
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        return None
