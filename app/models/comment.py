"""评论模型。"""
from tortoise import fields, models


class Comment(models.Model):
    """文章评论（0=待审核, 1=已通过, 2=已拒绝）。"""

    id = fields.IntField(primary_key=True)
    article_id = fields.IntField(index=True, description="文章 id")
    user_id = fields.IntField(null=True, description="评论者用户 id")
    username = fields.CharField(max_length=255, null=True, description="显示名")
    content = fields.TextField(description="评论内容")
    status = fields.IntField(default=0, description="0=待审核, 1=已通过, 2=已拒绝")
    created = fields.DatetimeField(auto_now_add=True, description="时间")

    class Meta:
        table = "comments"

    def __str__(self) -> str:
        return f"#{self.id} {self.username}"
