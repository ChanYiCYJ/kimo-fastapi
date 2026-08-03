"""通用 CRUD 基类，减少重复的增删改查代码。"""
from typing import Any, Generic, TypeVar

from tortoise.models import Model

ModelType = TypeVar("ModelType", bound=Model)


class CRUDBase(Generic[ModelType]):
    """针对 Tortoise 模型的通用 CRUD。"""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, id: int) -> ModelType | None:
        """按主键查询。"""
        return await self.model.get_or_none(id=id)

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> list[ModelType]:
        """分页/过滤查询。"""
        return await self.model.filter(**filters).offset(skip).limit(limit)

    async def create(self, obj_in: dict) -> ModelType:
        """新增。"""
        return await self.model.create(**obj_in)

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """更新（obj_in 为要更新的字段字典）。"""
        await db_obj.update_from_dict(obj_in).save()
        return db_obj

    async def remove(self, id: int) -> None:
        """按主键删除。"""
        await self.model.filter(id=id).delete()
