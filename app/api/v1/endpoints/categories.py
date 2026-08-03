"""分类接口。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.category import CategoryCreate, CategoryOut
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
