"""用户模型，映射现有表 userinfo。"""
from tortoise import fields, models


class UserInfo(models.Model):
    """用户表（Kimo 原项目 userinfo）。"""

    id = fields.IntField(primary_key=True)
    email = fields.CharField(max_length=255, unique=True, description="邮箱")
    password = fields.CharField(max_length=255, description="密码哈希")
    user_name = fields.CharField(max_length=255, null=True, description="用户名")
    role = fields.SmallIntField(default=1, description="0=管理员, 1=普通用户")

    class Meta:
        table = "userinfo"

    def __str__(self) -> str:
        return self.user_name or self.email
