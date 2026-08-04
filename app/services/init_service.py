"""初始化服务：默认管理员、注册开关等。

- `ensure_default_admin`：启动时确保至少存在一个管理员（role=0）
- `is_register_allowed`：判断站点是否开放注册
"""
import logging

from tortoise.exceptions import IntegrityError

from app.core.config import settings
from app.core.security import hash_password
from app.crud.user import user as user_crud
from app.models.user import UserInfo
from app.services import setting_service

logger = logging.getLogger("uvicorn.error")


async def ensure_default_admin() -> None:
    """启动时确保存在至少一个管理员（role=0）。

    注意：后端【不会】通过注册创建管理员（注册接口一律 role=1）。
    因此这里在首次启动时，若库中尚无任何 role=0 用户，则自动创建初始管理员，
    否则后台将无法登录。

    默认账号（可用环境变量覆盖）：
        ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD
    默认值：admin / admin@kimo.dev / admin123
    安全提醒：部署后请务必通过环境变量修改 ADMIN_PASSWORD。
    """
    if not settings.AUTO_CREATE_ADMIN:
        logger.info("AUTO_CREATE_ADMIN=False，跳过自动创建管理员")
        return
    if await UserInfo.filter(role=0).first():
        # 已存在管理员，无需创建
        return
    try:
        await user_crud.create(
            {
                "user_name": settings.ADMIN_USERNAME,
                "email": settings.ADMIN_EMAIL,
                "password": hash_password(settings.ADMIN_PASSWORD),
                "role": 0,
            }
        )
        logger.warning(
            "已自动创建默认管理员：%s / %s（密码来自 ADMIN_PASSWORD，请尽快修改！）",
            settings.ADMIN_USERNAME,
            settings.ADMIN_EMAIL,
        )
    except IntegrityError:
        # 并发启动或账号恰好已存在，忽略
        logger.info("默认管理员已存在，跳过创建")


async def is_register_allowed() -> bool:
    """是否开放注册。

    优先级：站点设置 `allow_register`（"0"/"false" = 关闭）
            > 环境变量 `ALLOW_REGISTER`（默认 True）。
    站点设置可在后台「站点设置」中维护（前端会写入 allow_register 键）。
    """
    val = await setting_service.get_setting("allow_register")
    if val is not None:
        return str(val).strip().lower() not in ("0", "false", "off", "no", "")
    return settings.ALLOW_REGISTER
