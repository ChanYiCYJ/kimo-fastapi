"""站点设置数据访问。"""
from tortoise import fields

from app.crud.base import CRUDBase
from app.models.setting import Setting


class CRUDSetting(CRUDBase[Setting]):
    """设置表操作（主键为 key，而非 id）。"""

    async def get(self, id: int) -> Setting | None:  # type: ignore[override]
        # 主键是 key，id 无业务意义，这里统一用 key 查询
        raise NotImplementedError("请使用 get_by_key")

    async def create(self, key: str, value: str) -> Setting:
        # 原表 id 列为 NOT NULL 且无自增，这里显式填 0
        return await self.model.create(key=key, value=value, id=0)

    async def get_by_key(self, key: str) -> Setting | None:
        return await self.model.get_or_none(pk=key)

    async def set_value(self, key: str, value: str) -> Setting:
        """存在则更新，不存在则创建。"""
        obj = await self.get_by_key(key)
        if obj:
            obj.value = value
            await obj.save(update_fields=["value"])
            return obj
        return await self.create(key, value)

    async def remove_by_key(self, key: str) -> None:
        await self.model.filter(pk=key).delete()


setting = CRUDSetting(Setting)
