"""媒体数据访问。"""
from app.crud.base import CRUDBase
from app.models.media import Media


class CRUDMedia(CRUDBase[Media]):
    """媒体表操作。"""

    async def get_multi_page(
        self,
        *,
        page: int = 1,
        page_size: int = 24,
        mime_type: str | None = None,
    ) -> list[Media]:
        """分页查询（按上传时间倒序），支持按 MIME 类型前缀过滤。"""
        query = self.model.all().order_by("-created")
        if mime_type:
            query = query.filter(mime__startswith=mime_type)
        return await query.offset((page - 1) * page_size).limit(page_size)

    async def count(self, *, mime_type: str | None = None) -> int:
        query = self.model.all()
        if mime_type:
            query = query.filter(mime__startswith=mime_type)
        return await query.count()


media = CRUDMedia(Media)
