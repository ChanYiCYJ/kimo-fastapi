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
