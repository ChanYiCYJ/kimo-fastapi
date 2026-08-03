"""分类模型，映射现有表 categories。"""
from tortoise import fields, models


class Category(models.Model):
    """文章分类。"""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, description="分类名")
    slug = fields.CharField(max_length=50, unique=True, description="拼音别名")
    description = fields.CharField(max_length=200, null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "categories"

    def __str__(self) -> str:
        return self.name
