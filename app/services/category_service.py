"""分类业务。"""
from fastapi import HTTPException

from app.crud.category import category as category_crud
from app.utils.pinyin import translate


async def list_categories() -> list:
    return await category_crud.get_multi()


async def create_category(payload) -> dict:
    """创建分类，slug 为空时自动按拼音生成。"""
    slug = payload.slug or translate(payload.name)
    if await category_crud.get_by_slug(slug):
        raise HTTPException(status_code=400, detail=f"slug 已存在: {slug}")
    obj = await category_crud.create(
        {"name": payload.name, "slug": slug, "description": payload.description}
    )
    return {
        "id": obj.id,
        "name": obj.name,
        "slug": obj.slug,
        "description": obj.description,
        "created_at": obj.created_at,
    }


async def update_category(category_id: int, payload) -> dict:
    """更新分类（字段可选，slug 为空时按名称重新生成）。"""
    obj = await category_crud.get(category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="分类不存在")
    data: dict = {}
    if payload.name is not None:
        data["name"] = payload.name
    if payload.description is not None:
        data["description"] = payload.description
    if payload.slug is not None:
        slug = payload.slug or translate(payload.name or obj.name)
        dup = await category_crud.get_by_slug(slug)
        if dup and dup.id != category_id:
            raise HTTPException(status_code=400, detail=f"slug 已存在: {slug}")
        data["slug"] = slug
    obj = await category_crud.update(obj, data)
    return {
        "id": obj.id,
        "name": obj.name,
        "slug": obj.slug,
        "description": obj.description,
        "created_at": obj.created_at,
    }


async def delete_category(category_id: int) -> None:
    """删除分类。"""
    obj = await category_crud.get(category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="分类不存在")
    await category_crud.remove(category_id)
