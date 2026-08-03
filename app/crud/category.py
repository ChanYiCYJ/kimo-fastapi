"""分类数据访问。"""
from app.crud.base import CRUDBase
from app.models.category import Category


class CRUDCategory(CRUDBase[Category]):
    """分类表操作。"""

    async def get_by_slug(self, slug: str) -> Category | None:
        return await self.model.get_or_none(slug=slug)

    async def get_by_name(self, name: str) -> Category | None:
        return await self.model.get_or_none(name=name)


category = CRUDCategory(Category)
