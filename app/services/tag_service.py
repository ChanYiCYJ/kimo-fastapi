"""标签业务。"""
from fastapi import HTTPException
from tortoise import Tortoise

from app.crud.tag import tag as tag_crud


async def list_tags() -> list:
    return await tag_crud.get_multi(limit=200)


async def create_tag(payload) -> dict:
    """创建标签，重名自动返回已有标签。"""
    tag_obj = await tag_crud.get_by_name(payload.tag_name)
    if tag_obj:
        raise HTTPException(status_code=400, detail="标签已存在")
    tag_obj = await tag_crud.create({"tag_name": payload.tag_name})
    return {"id": tag_obj.id, "tag_name": tag_obj.tag_name}


async def update_tag(tag_id: int, payload) -> dict:
    """更新标签（字段可选）。"""
    obj = await tag_crud.get(tag_id)
    if not obj:
        raise HTTPException(status_code=404, detail="标签不存在")
    if payload.tag_name is not None:
        dup = await tag_crud.get_by_name(payload.tag_name)
        if dup and dup.id != tag_id:
            raise HTTPException(status_code=400, detail="标签已存在")
        obj = await tag_crud.update(obj, {"tag_name": payload.tag_name})
    return {"id": obj.id, "tag_name": obj.tag_name}


async def delete_tag(tag_id: int) -> None:
    """删除标签，并清理文章关联。"""
    obj = await tag_crud.get(tag_id)
    if not obj:
        raise HTTPException(status_code=404, detail="标签不存在")
    conn = Tortoise.get_connection("default")
    await conn.execute_query(
        "DELETE FROM article_tags WHERE tag_id = %s", [tag_id]
    )
    await tag_crud.remove(tag_id)
