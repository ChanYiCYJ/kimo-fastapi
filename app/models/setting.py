"""站点设置模型，映射现有表 setting（主键为 key）。"""
from tortoise import fields, models


class Setting(models.Model):
    """站点配置键值对。"""

    key = fields.CharField(max_length=100, primary_key=True, description="配置键")
    value = fields.TextField(description="配置值")
    # 原表还有一个无自增的 id 普通列，仅做展示用
    id = fields.IntField(description="原表 id 列")

    class Meta:
        table = "setting"

    def __str__(self) -> str:
        return f"{self.key}={self.value}"
