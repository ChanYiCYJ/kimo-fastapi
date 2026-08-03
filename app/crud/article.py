"""文章数据访问。"""
from app.crud.base import CRUDBase
from app.models.article import Article


class CRUDArticle(CRUDBase[Article]):
    """文章表操作。"""

    PAGE_SIZE = 5  # 与 Kimo 原项目一致

    def _with_relations(self, query):
        """预加载分类，避免 N+1 查询。

        注意：标签通过 article_tags 原生 JOIN 加载（见 service 层），
        因为 article_tags 表为复合主键，Tortoise 无法 prefetch。
        """
        return query.select_related("category")

    async def get(self, id: int) -> Article | None:
        return await self._with_relations(self.model.get_or_none(id=id))

    async def get_multi_page(
        self, *, page: int = 1, category_id: int | None = None, keyword: str | None = None
    ) -> list[Article]:
        """分页查询（每页 5 条），支持分类过滤与标题关键词搜索。"""
        query = self._with_relations(self.model.all())
        if category_id is not None:
            query = query.filter(category_id=category_id)
        if keyword:
            query = query.filter(title__icontains=keyword)
        return await query.offset((page - 1) * self.PAGE_SIZE).limit(self.PAGE_SIZE)

    async def count(
        self, *, category_id: int | None = None, keyword: str | None = None
    ) -> int:
        """统计总数（支持同样过滤）。"""
        query = self.model.all()
        if category_id is not None:
            query = query.filter(category_id=category_id)
        if keyword:
            query = query.filter(title__icontains=keyword)
        return await query.count()


article = CRUDArticle(Article)
