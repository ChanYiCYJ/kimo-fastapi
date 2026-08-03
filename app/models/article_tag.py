"""文章-标签关联模型，映射现有表 article_tags。

该表为复合主键 (article_id, tag_id)，Tortoise 不支持复合主键写入，
因此这里仅用于查询；写入关联在 service 层使用原生 SQL 处理。
"""
from tortoise import fields, models


class ArticleTag(models.Model):
    """文章与标签的多对多关联（只读）。"""

    article = fields.ForeignKeyField(
        "models.Article", source_field="article_id", related_name="article_tag_links"
    )
    tag = fields.ForeignKeyField(
        "models.Tag", source_field="tag_id", related_name="article_tag_links"
    )

    class Meta:
        table = "article_tags"
        pk = False  # 复合主键，只读

    def __str__(self) -> str:
        return f"Article#{self.article_id}-Tag#{self.tag_id}"
