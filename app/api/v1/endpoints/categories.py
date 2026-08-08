"""分类接口。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.common import ApiResponse
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("", response_model=ApiResponse[list[CategoryOut]], summary="分类列表")
async def list_categories() -> dict:
    data = await category_service.list_categories()
    return {"data": data}


@router.post("", response_model=ApiResponse[CategoryOut], summary="创建分类（管理员）")
async def create_category(payload: CategoryCreate, _: CurrentAdmin) -> dict:
    data = await category_service.create_category(payload)
    return {"data": data}


@router.put("/{category_id}", response_model=ApiResponse[CategoryOut], summary="更新分类（管理员）")
async def update_category(category_id: int, payload: CategoryUpdate, _: CurrentAdmin) -> dict:
    data = await category_service.update_category(category_id, payload)
    return {"data": data}


@router.delete("/{category_id}", response_model=ApiResponse, summary="删除分类（管理员）")
async def delete_category(category_id: int, _: CurrentAdmin) -> dict:
    await category_service.delete_category(category_id)
    return {"message": "删除成功"}
