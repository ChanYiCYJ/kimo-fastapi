"""标签数据访问。"""
from app.crud.base import CRUDBase
from app.models.tag import Tag


class CRUDTag(CRUDBase[Tag]):
    """标签表操作。"""

    async def get_by_name(self, tag_name: str) -> Tag | None:
        return await self.model.get_or_none(tag_name=tag_name)

    async def get_or_create(self, tag_name: str) -> Tag:
        """按名获取，不存在则创建。"""
        tag = await self.get_by_name(tag_name)
        if tag:
            return tag
        return await self.model.create(tag_name=tag_name)


tag = CRUDTag(Tag)
