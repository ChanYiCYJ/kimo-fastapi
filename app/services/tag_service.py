"""标签业务。"""
from fastapi import HTTPException

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
