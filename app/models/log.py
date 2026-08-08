"""系统操作日志模型。"""
from tortoise import fields, models


class SysLog(models.Model):
    """管理员操作日志（记录写操作：增删改）。"""

    id = fields.IntField(primary_key=True)
    created = fields.DatetimeField(auto_now_add=True, description="时间")
    user_id = fields.IntField(null=True, description="用户 id")
    username = fields.CharField(max_length=255, null=True, description="用户名")
    action = fields.CharField(max_length=50, description="操作（CREATE/UPDATE/DELETE）")
    method = fields.CharField(max_length=10, description="HTTP 方法")
    path = fields.CharField(max_length=500, description="路径")
    status = fields.IntField(default=0, description="状态码")
    ms = fields.IntField(default=0, description="耗时（毫秒）")
    ip = fields.CharField(max_length=64, null=True, description="IP")

    class Meta:
        table = "sys_log"

    def __str__(self) -> str:
        return f"{self.action} {self.path}"
