"""标签接口。"""
from fastapi import APIRouter

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.schemas.tag import TagCreate, TagOut
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("", response_model=ApiResponse[list[TagOut]], summary="标签列表")
async def list_tags() -> dict:
    data = await tag_service.list_tags()
    return {"data": data}


@router.post("", response_model=ApiResponse[TagOut], summary="创建标签（管理员）")
async def create_tag(payload: TagCreate, _: CurrentAdmin) -> dict:
    data = await tag_service.create_tag(payload)
    return {"data": data}
