"""为新增表（media/log/comment）创建缺失表结构。

新增表不在 Kimo 原有 Flask 表结构中，需手动建表。
使用 Tortoise generate_schemas(safe=True)（CREATE TABLE IF NOT EXISTS），
对已有表无副作用，可重复执行。

用法（项目根目录）：
    python -m deploy.create_new_tables
"""
import asyncio

from app.core.database import TORTOISE_ORM
from tortoise import Tortoise


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    # 只创建缺失的表（safe=True → CREATE TABLE IF NOT EXISTS）
    await Tortoise.generate_schemas(safe=True)
    created = await Tortoise.get_connection("default").execute_query(
        "SHOW TABLES LIKE 'media'"
    )
    print("media 表存在:", bool(created[1]))
    created2 = await Tortoise.get_connection("default").execute_query(
        "SHOW TABLES LIKE 'sys_log'"
    )
    print("sys_log 表存在:", bool(created2[1]))
    created3 = await Tortoise.get_connection("default").execute_query(
        "SHOW TABLES LIKE 'comments'"
    )
    print("comments 表存在:", bool(created3[1]))
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
