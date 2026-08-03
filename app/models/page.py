"""页面模型，映射现有表 page。"""
from tortoise import fields, models


class Page(models.Model):
    """自定义页面（type: markdown / html / list / link）。"""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, description="页面名称")
    content = fields.TextField(null=True, description="内容")
    type = fields.CharField(max_length=100, description="页面类型")
    status = fields.IntField(default=0, description="状态")

    class Meta:
        table = "page"

    def __str__(self) -> str:
        return self.name
