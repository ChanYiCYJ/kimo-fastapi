"""页面接口。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.schemas.page import PageCreate, PageOut, PageUpdate
from app.services import page_service

router = APIRouter(prefix="/pages", tags=["页面"])


@router.get("", response_model=ApiResponse[list[PageOut]], summary="页面列表")
async def list_pages() -> dict:
    data = await page_service.list_pages()
    return {"data": data}


@router.get("/by-name/{name}", response_model=ApiResponse[PageOut], summary="按名称获取页面（前台）")
async def get_page_by_name(name: str) -> dict:
    data = await page_service.get_page_by_name(name)
    return {"data": data}


@router.get("/{page_id}", response_model=ApiResponse[PageOut], summary="页面详情")
async def get_page(page_id: int) -> dict:
    data = await page_service.get_page(page_id)
    return {"data": data}


@router.post("", response_model=ApiResponse[PageOut], summary="创建页面（管理员）")
async def create_page(payload: PageCreate, _: CurrentAdmin) -> dict:
    data = await page_service.create_page(payload)
    return {"data": data}


@router.put("/{page_id}", response_model=ApiResponse[PageOut], summary="更新页面（管理员）")
async def update_page(page_id: int, payload: PageUpdate, _: CurrentAdmin) -> dict:
    data = await page_service.update_page(page_id, payload)
    return {"data": data}


@router.delete("/{page_id}", response_model=ApiResponse, summary="删除页面（管理员）")
async def delete_page(page_id: int, _: CurrentAdmin) -> dict:
    await page_service.delete_page(page_id)
    return {"message": "删除成功"}
