"""操作日志数据访问。"""
from app.crud.base import CRUDBase
from app.models.log import SysLog


class CRUDLog(CRUDBase[SysLog]):
    """日志表操作。"""

    async def get_multi_page(
        self, *, page: int = 1, page_size: int = 20, action: str | None = None
    ) -> list[SysLog]:
        query = self.model.all().order_by("-created")
        if action:
            query = query.filter(action=action)
        return await query.offset((page - 1) * page_size).limit(page_size)

    async def count(self, *, action: str | None = None) -> int:
        query = self.model.all()
        if action:
            query = query.filter(action=action)
        return await query.count()


log = CRUDLog(SysLog)
