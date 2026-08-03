"""文章模型，映射现有表 articles。"""
from tortoise import fields, models


class Article(models.Model):
    """文章。"""

    id = fields.IntField(primary_key=True)
    created = fields.DatetimeField(auto_now_add=True, description="创建时间")
    title = fields.TextField(description="标题")
    content = fields.TextField(description="Markdown 内容")
    category = fields.ForeignKeyField(
        "models.Category",
        related_name="articles",
        source_field="category_id",
        null=True,
        on_delete=fields.SET_NULL,
        description="所属分类",
    )
    description = fields.TextField(null=True, description="摘要")
    cover_image = fields.TextField(null=True, description="封面图 URL")

    class Meta:
        table = "articles"
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.title
