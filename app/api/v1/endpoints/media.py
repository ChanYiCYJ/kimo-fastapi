"""媒体库接口（管理员）。"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentAdmin
from app.schemas.common import ApiResponse
from app.schemas.media import MediaListResult, MediaOut
from app.services import media_service

router = APIRouter(prefix="/media", tags=["媒体"])


@router.get("", response_model=ApiResponse[MediaListResult], summary="媒体列表（管理员）")
async def list_media(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(24, ge=1, le=100, description="每页数量"),
    mime_type: str | None = Query(None, description="按类型前缀过滤（如 image/video）"),
    _: CurrentAdmin = None,
) -> dict:
    data = await media_service.list_media(
        page=page, page_size=page_size, mime_type=mime_type
    )
    return {"data": data}


@router.delete("/{media_id}", response_model=ApiResponse, summary="删除媒体（管理员）")
async def delete_media(media_id: int, _: CurrentAdmin = None) -> dict:
    await media_service.delete_media(media_id)
    return {"message": "删除成功"}
