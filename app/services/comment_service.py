"""评论业务。"""
import math

from fastapi import HTTPException

from app.crud.comment import comment as comment_crud


def _to_out(c) -> dict:
    return {
        "id": c.id,
        "article_id": c.article_id,
        "user_id": c.user_id,
        "username": c.username,
        "content": c.content,
        "status": c.status,
        "created": c.created,
    }


async def list_by_article(article_id: int) -> list:
    """前台：按文章返回已通过的评论。"""
    items = await comment_crud.list_by_article(article_id)
    return [_to_out(c) for c in items]


async def create_comment(payload, user) -> dict:
    """前台：提交评论（默认待审核）。"""
    obj = await comment_crud.create(
        {
            "article_id": payload.article_id,
            "user_id": user.id,
            "username": user.user_name or user.email,
            "content": payload.content,
            "status": 0,
        }
    )
    return _to_out(obj)


async def list_all(page: int = 1, page_size: int = 20, status: int | None = None) -> dict:
    """后台：全部评论分页。"""
    items = await comment_crud.get_multi_page(page=page, page_size=page_size, status=status)
    total = await comment_crud.count(status=status)
    total_page = max(1, math.ceil(total / page_size))
    return {
        "items": [_to_out(c) for c in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_page": total_page,
    }


async def update_status(comment_id: int, status: int) -> dict:
    obj = await comment_crud.get(comment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="评论不存在")
    obj = await comment_crud.update(obj, {"status": status})
    return _to_out(obj)


async def delete_comment(comment_id: int) -> None:
    obj = await comment_crud.get(comment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="评论不存在")
    await comment_crud.remove(comment_id)
