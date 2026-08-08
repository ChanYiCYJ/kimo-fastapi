"""评论数据访问。"""
from app.crud.base import CRUDBase
from app.models.comment import Comment


class CRUDComment(CRUDBase[Comment]):
    """评论表操作。"""

    async def get_multi_page(
        self, *, page: int = 1, page_size: int = 20, status: int | None = None
    ) -> list[Comment]:
        query = self.model.all().order_by("-created")
        if status is not None:
            query = query.filter(status=status)
        return await query.offset((page - 1) * page_size).limit(page_size)

    async def count(self, *, status: int | None = None) -> int:
        query = self.model.all()
        if status is not None:
            query = query.filter(status=status)
        return await query.count()

    async def list_by_article(self, article_id: int) -> list[Comment]:
        """按文章返回已通过的评论（按时间正序）。"""
        return await self.model.filter(article_id=article_id, status=1).order_by("created")


comment = CRUDComment(Comment)
