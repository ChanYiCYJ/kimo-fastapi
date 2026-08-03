"""数据库连接与初始化（Tortoise ORM）。

- `TORTOISE_ORM` 同时供 aerich 迁移工具引用。
- `init_db` / `close_db` 在应用生命周期中调用。
"""
from tortoise import Tortoise

from app.core.config import settings

# aerich 迁移工具引用：tortoise_orm = "app.core.database.TORTOISE_ORM"
TORTOISE_ORM: dict = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            # 注意：模块路径要能被 import，aerich.models 是迁移记录表
            "models": [
                "app.models.user",
                "app.models.category",
                "app.models.tag",
                "app.models.article",
                "app.models.article_tag",
                "app.models.page",
                "app.models.setting",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}

# MySQL 时启用连接池（与根目录 test1.py 的 db_pool 一致）
if settings.DB_ENGINE == "mysql":
    TORTOISE_ORM["db_pool"] = {
        "maxsize": settings.DB_POOL_MAX_SIZE,
        "minsize": settings.DB_POOL_MIN_SIZE,
        "idle_timeout": settings.DB_POOL_IDLE_TIMEOUT,
    }


async def init_db() -> None:
    """初始化数据库连接。

    表结构已由 Kimo 原项目建好，这里直接连接复用，不做自动建表，
    结构变更统一走 aerich 迁移。
    """
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db() -> None:
    """关闭所有数据库连接。"""
    await Tortoise.close_connections()
