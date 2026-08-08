"""媒体文件模型（媒体库）。"""
from tortoise import fields, models


class Media(models.Model):
    """媒体库文件：上传即入库，便于管理/删除。"""

    id = fields.IntField(primary_key=True)
    filename = fields.CharField(max_length=255, description="存储文件名")
    original_name = fields.CharField(max_length=255, null=True, description="原始文件名")
    url = fields.CharField(max_length=500, description="访问路径（/static/uploads/...）")
    size = fields.IntField(default=0, description="文件大小（字节）")
    mime = fields.CharField(max_length=100, null=True, description="MIME 类型")
    uploader_id = fields.IntField(null=True, description="上传者用户 id")
    created = fields.DatetimeField(auto_now_add=True, description="上传时间")

    class Meta:
        table = "media"

    def __str__(self) -> str:
        return self.filename
