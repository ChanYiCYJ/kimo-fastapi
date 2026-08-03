"""页面数据访问。"""
from app.crud.base import CRUDBase
from app.models.page import Page


class CRUDPage(CRUDBase[Page]):
    """页面表操作。"""

    async def get_by_name(self, name: str) -> Page | None:
        return await self.model.get_or_none(name=name)


page = CRUDPage(Page)
