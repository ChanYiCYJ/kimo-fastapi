"""标签模型，映射现有表 tags。"""
from tortoise import fields, models


class Tag(models.Model):
    """文章标签。"""

    id = fields.IntField(primary_key=True)
    tag_name = fields.CharField(max_length=50, unique=True, description="标签名")

    class Meta:
        table = "tags"

    def __str__(self) -> str:
        return self.tag_name
